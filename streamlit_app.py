from __future__ import annotations

import html
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from nora import __ontology_version__, __rule_set_version__, __version__
from nora.assertions import (
    REVIEW_STATUS_OPTIONS,
    apply_reviewed_assertions,
    assertion_table_rows,
    assertions_from_table_rows,
    extract_assertions_from_documents,
    reviewed_assertion_conflicts,
)
from nora.cases import CASE_BUILDERS, load_case
from nora.consulting_cases import CONSULTING_CASES, load_consulting_assessment
from nora.engine import ROLE_DEFINITIONS, evaluate
from nora.i18n import (
    ASSERTION_COLUMNS,
    PAGE_IDS,
    assertion_field_label,
    audit_action_label,
    audit_detail_label,
    case_label,
    category_label,
    internalize_assertion_row,
    localize_assertion_row,
    localize_document_row,
    localize_result,
    page_label,
    review_status_label,
    role_definition,
    text as i18n_text,
    value_label,
)
from nora.evidence import (
    DocumentRecord,
    EvidenceAssertion,
    document_inventory_row,
    extract_document,
)
from nora.models import (
    AIModelCard,
    AssessmentInput,
    ContextOfUse,
    NAMAssayCard,
    ProductContext,
    SupportingEvidence,
)
from nora.ontology import build_jsonld, build_turtle
from nora.projects import ProjectBundle, ProjectStore, load_project_json, project_json_bytes
from nora.reports import build_gap_csv, build_markdown_report, build_pdf_report
from nora.ui import (
    inject_design_system,
    render_brand_header,
    render_advisory_card,
    render_consulting_case_card,
    render_footer_notice,
    render_next_action,
    render_page_header,
    render_pipeline,
    render_role_ladder,
    render_section_band,
    render_status_strip as render_kpi_strip,
    role_tone,
    safe as safe_html,
)


APP_ROOT = Path(__file__).resolve().parent
RULE_CATALOG_PATH = APP_ROOT / "data" / "rule_catalog.json"
AI_RULE_CATALOG_PATH = APP_ROOT / "data" / "ai_credibility_rule_catalog.json"
FLAGSHIP_REFERENCE_PATH = APP_ROOT / "data" / "flagship_reference_registry.json"
ONTOLOGY_CORE_PATH = APP_ROOT / "ontology" / "tg_pto_et_core.ttl"
ONTOLOGY_SHAPES_PATH = APP_ROOT / "ontology" / "tg_pto_et_shapes.ttl"

st.set_page_config(
    page_title="ToxiGuard NORA EarlyTox",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_design_system()


NAV_PAGES = PAGE_IDS
NAV_PAGE_KEY = "nav_page"
PENDING_NAV_PAGE_KEY = "pending_nav_page"
LEGACY_NAV_PAGES = {
    "프로젝트 개요": "overview",
    "문서 근거": "documents",
    "근거 검토": "assertions",
    "평가 입력": "assessment",
    "결과·보고서": "results",
    "규칙·온톨로지": "rules",
}



def language() -> str:
    selected = st.session_state.get("nora_language", "한국어")
    return "en" if selected == "English" else "ko"


def L(ko: str, en: str) -> str:
    return en if language() == "en" else ko


def T(key: str, **kwargs: Any) -> str:
    return i18n_text(key, language(), **kwargs)


def fmt(value: Any) -> str:
    return value_label(value, language())


def _page(page_id: str) -> str:
    return page_label(page_id, language())


def _normalize_nav_page(page: object) -> str:
    page_id = LEGACY_NAV_PAGES.get(page, page) if isinstance(page, str) else page
    return page_id if page_id in NAV_PAGES else "overview"


def _apply_pending_widget_state() -> None:
    pending_nav_page = st.session_state.pop(PENDING_NAV_PAGE_KEY, None)
    if pending_nav_page is not None:
        normalized_page = _normalize_nav_page(pending_nav_page)
    else:
        normalized_page = _normalize_nav_page(st.session_state.get(NAV_PAGE_KEY))
    if st.session_state.get(NAV_PAGE_KEY) != normalized_page:
        st.session_state[NAV_PAGE_KEY] = normalized_page


@st.cache_data
def consulting_reference_registry() -> dict[str, dict[str, Any]]:
    if not FLAGSHIP_REFERENCE_PATH.exists():
        return {}
    try:
        return json.loads(FLAGSHIP_REFERENCE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


@st.cache_resource
def get_store() -> ProjectStore:
    data_dir = Path(os.environ.get("NORA_DATA_DIR", APP_ROOT / ".nora_data"))
    return ProjectStore(data_dir / "projects.db")


def project() -> ProjectBundle:
    if "nora_project" not in st.session_state:
        st.session_state.nora_project = ProjectBundle.new(name=L("새 EarlyTox 프로젝트", "New EarlyTox Project"))
    return st.session_state.nora_project


def _queue_navigation(page: str) -> None:
    st.session_state[PENDING_NAV_PAGE_KEY] = _normalize_nav_page(page)


def set_project(value: ProjectBundle, page: str = "overview") -> None:
    st.session_state.nora_project = value
    st.session_state.assessment_result = None
    _queue_navigation(page)


def result():
    return st.session_state.get("assessment_result")


def invalidate_result() -> None:
    st.session_state.assessment_result = None
    project().last_result = None


def add_event(action: str, detail: str) -> None:
    project().add_event(action, detail, project().owner or "현재 사용자")


def _optional_number(
    value: object,
    low: float | None = None,
    high: float | None = None,
) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        number = float(text)
    except (TypeError, ValueError):
        return None
    if low is not None:
        number = max(low, number)
    if high is not None:
        number = min(high, number)
    return number


def _optional_float(value: object) -> float | None:
    """Parse a percentage and constrain it to 0–100."""
    return _optional_number(value, 0.0, 100.0)


def _optional_int(value: object) -> int | None:
    number = _optional_number(value, 0.0, None)
    return int(number) if number is not None else None


def _status_counts() -> dict[str, int]:
    counts = {status: 0 for status in REVIEW_STATUS_OPTIONS}
    for assertion in project().assertions:
        counts[assertion.review_status] = counts.get(assertion.review_status, 0) + 1
    return counts


def header() -> None:
    left, right = st.columns([8.25, 1.75], gap="medium")
    with left:
        render_brand_header(
            subtitle=T("header_description"),
            version=__version__,
            ontology_version=__ontology_version__,
            rule_version=__rule_set_version__,
            eyebrow=L("비임상 근거 보증", "Nonclinical evidence assurance"),
            project_name=project().project_name,
        )
    with right:
        st.markdown(
            f'<div class="nora-language-anchor"><span>{safe_html(T("language"))}</span>'
            f'<strong>{safe_html(L("한국어 / English", "Korean / English"))}</strong></div>',
            unsafe_allow_html=True,
        )
        st.radio(
            T("language"),
            ["한국어", "English"],
            index=0 if language() == "ko" else 1,
            horizontal=True,
            key="nora_language",
            label_visibility="collapsed",
        )
    st.markdown(
        f'<div class="nora-trust-line"><strong>{safe_html(T("tagline"))}</strong>'
        f'<span>{safe_html(T("header_principle"))}</span></div>',
        unsafe_allow_html=True,
    )


def status_strip() -> None:
    p = project()
    counts = _status_counts()
    assessed = result()
    approved_count = counts.get("승인", 0) + counts.get("수정", 0)
    role_label = assessed.evidence_role_code if assessed else T("not_assessed")
    role_value = assessed.evidence_role if assessed else None
    render_kpi_strip(
        [
            {
                "label": T("documents"),
                "value": T("items_count", count=len(p.documents)),
                "sub": L("추적 가능한 근거 파일", "Traceable evidence files"),
                "accent": "accent-blue",
            },
            {
                "label": T("assertions"),
                "value": T("items_count", count=len(p.assertions)),
                "sub": L("구조화된 근거 주장", "Structured evidence claims"),
                "accent": "accent-blue",
            },
            {
                "label": T("approved_corrected"),
                "value": T("items_count", count=approved_count),
                "sub": L("판정에 사용 가능한 검토 근거", "Reviewed evidence eligible for assessment"),
                "accent": "accent-amber",
            },
            {
                "label": T("current_role"),
                "value": role_label,
                "sub": L("현재 근거 사용범위", "Current evidence-use boundary"),
                "role": "true",
            },
        ],
        role=role_value,
    )

def pipeline(page: str) -> None:
    if page == "consulting":
        render_pipeline(
            [
                (L("고객", "Client"), L("조직·개발단계", "Segment & stage")),
                (L("목적", "Objective"), L("결정해야 할 질문", "Decision question")),
                (L("근거", "Evidence"), L("보유자료·불확실성", "Evidence & uncertainty")),
                (L("자문", "Advisory"), L("산출물·다음 단계", "Deliverables & next step")),
            ],
            1,
        )
        return
    core_pages = ["overview", "documents", "assertions", "assessment", "results", "rules"]
    steps = [
        (L("프로젝트", "Project"), L("질문·맥락 정의", "Question & context")),
        (L("문서", "Documents"), L("AI/NAM/PK 근거", "AI/NAM/PK evidence")),
        (L("검토", "Review"), L("승인·수정·거절", "Approve · correct · reject")),
        (L("평가", "Assessment"), L("Gate·Data Gap", "Gates · Data Gaps")),
        (L("결과", "Results"), "Evidence Role R0–R5"),
        (L("논리", "Logic"), L("규칙·온톨로지", "Rules · ontology")),
    ]
    active_index = core_pages.index(page) if page in core_pages else 0
    render_pipeline(steps, active_index)

def sidebar() -> str:
    _apply_pending_widget_state()
    p = project()
    with st.sidebar:
        st.markdown(
            f"""
<div class="nora-side-brand">
  <div class="nora-side-brand-top">
    <div class="nora-side-mark">N</div>
    <div><strong>NORA EarlyTox</strong><span>v{safe_html(__version__)} · {safe_html(__ontology_version__)}</span></div>
  </div>
  <div class="nora-side-project"><span>{safe_html(T('project'))}</span><strong>{safe_html(p.project_name)}</strong></div>
</div>
<div class="nora-side-section">{safe_html(T('workspace'))}</div>
""",
            unsafe_allow_html=True,
        )

        page = st.radio(
            T("workspace"),
            NAV_PAGES,
            format_func=lambda page_id: _page(page_id),
            key=NAV_PAGE_KEY,
            label_visibility="collapsed",
        )

        st.markdown(f'<div class="nora-side-section">{safe_html(T("project_management"))}</div>', unsafe_allow_html=True)
        with st.expander(T("project_management"), expanded=False):
            name = st.text_input(T("project_name"), value=p.project_name, key=f"project_name_{p.project_id}")
            owner = st.text_input(T("project_owner"), value=p.owner, key=f"project_owner_{p.project_id}")
            description = st.text_area(T("project_description"), value=p.description, height=75, key=f"project_desc_{p.project_id}")
            if st.button(T("apply_metadata"), use_container_width=True, key=f"meta_apply_{p.project_id}"):
                p.project_name, p.owner, p.description = name.strip() or p.project_name, owner.strip(), description.strip()
                p.touch()
                add_event("프로젝트 메타데이터 수정", p.project_name)
                st.success(T("metadata_applied"))

            c1, c2 = st.columns(2)
            if c1.button(T("new_project"), use_container_width=True, key=f"new_project_{p.project_id}"):
                set_project(ProjectBundle.new(name=L("새 EarlyTox 프로젝트", "New EarlyTox Project")), "overview")
                st.rerun()
            if c2.button(T("local_save"), use_container_width=True, key=f"local_save_{p.project_id}"):
                try:
                    add_event("로컬 프로젝트 저장", str(get_store().path))
                    get_store().save(p)
                    st.success(T("saved_local"))
                except Exception as exc:
                    st.error(T("save_failed", error=exc))

            saved = get_store().list_projects()
            saved_map = {f"{item['project_name']} · {item['updated_at_utc'][:16]}": item["project_id"] for item in saved}
            none_option = "__none__"
            selected_saved = st.selectbox(
                T("saved_projects"),
                [none_option] + list(saved_map),
                format_func=lambda value: T("none_selected") if value == none_option else value,
                key=f"saved_project_selector_{language()}",
            )
            c3, c4 = st.columns(2)
            if c3.button(T("load"), use_container_width=True, disabled=selected_saved == none_option, key=f"load_saved_{p.project_id}"):
                loaded = get_store().load(saved_map[selected_saved])
                if loaded:
                    loaded.add_event("로컬 프로젝트 불러오기", loaded.project_name)
                    set_project(loaded)
                    st.rerun()
            if c4.button(T("delete"), use_container_width=True, disabled=selected_saved == none_option, key=f"delete_saved_{p.project_id}"):
                get_store().delete(saved_map[selected_saved])
                st.success(T("deleted_local"))
                st.rerun()

            project_upload = st.file_uploader(T("project_json_upload"), type=["json"], key=f"project_json_{p.project_id}")
            if project_upload and st.button(T("apply_json"), use_container_width=True, key=f"project_json_apply_{p.project_id}"):
                try:
                    loaded = load_project_json(project_upload.getvalue())
                    loaded.add_event("JSON 프로젝트 불러오기", project_upload.name)
                    set_project(loaded)
                    st.rerun()
                except Exception as exc:
                    st.error(T("project_json_error", error=exc))

            st.download_button(
                T("download_project_json"),
                project_json_bytes(p),
                file_name=f"{p.project_name.replace(' ','_')}.nora.json",
                mime="application/json",
                use_container_width=True,
                key=f"download_project_{p.project_id}",
            )

        st.markdown(
            f'<div class="nora-compact-note"><strong>{safe_html(_page("consulting"))}</strong><br>'
            f'{safe_html(L("고객 유형과 의사결정 목적별 사례는 전용 작업공간에서 비교할 수 있습니다.", "Compare client- and objective-specific cases in the dedicated advisory workspace."))}</div>',
            unsafe_allow_html=True,
        )

        with st.expander(T("golden_case"), expanded=False):
            demo = st.selectbox(
                T("synthetic_case"),
                list(CASE_BUILDERS),
                format_func=lambda value: case_label(value, language()),
                key="demo_selector",
            )
            if st.button(T("load_case"), use_container_width=True, key=f"load_case_{p.project_id}"):
                demo_project = ProjectBundle.new(name=case_label(demo, language()))
                demo_project.assessment_input = load_case(demo, language())
                demo_project.add_event("Golden Case 불러오기", demo)
                set_project(demo_project, "assessment")
                st.rerun()

        st.markdown(
            f'<div class="nora-side-note">{safe_html(T("prototype_note"))}</div>',
            unsafe_allow_html=True,
        )
    return page



def _next_action_state() -> tuple[str, str, str]:
    p = project()
    counts = _status_counts()
    cou = p.assessment_input.context_of_use
    if not cou.question_of_interest.strip():
        return (
            L("개발 질문을 먼저 정의하십시오", "Define the development question first"),
            L("Question of Interest와 Context of Use를 정하면 이후 문서와 모델 결과를 같은 결정 맥락에서 검토할 수 있습니다.", "Defining the Question of Interest and Context of Use keeps all subsequent evidence tied to the same decision."),
            "assessment",
        )
    if not p.documents and not p.assertions:
        return (
            L("추적 가능한 근거를 추가하십시오", "Add traceable evidence"),
            L("AI 모델 카드, NAM 보고서, PK/TK 또는 biodistribution 자료를 업로드하거나 수동 근거를 입력하십시오.", "Upload an AI model card, NAM report, PK/TK, or biodistribution evidence, or enter evidence manually."),
            "documents",
        )
    if counts.get("제안됨", 0) > 0:
        return (
            L("자동 추출 Assertion을 검토하십시오", "Review proposed Evidence Assertions"),
            L("제안된 값은 아직 판정에 사용되지 않습니다. 출처와 부정문·누락 표현을 확인한 뒤 승인·수정·거절하십시오.", "Proposed values do not affect the assessment until a human verifies the source, negation, and missing-data context."),
            "assertions",
        )
    if result() is None:
        return (
            L("구조화 평가를 저장하고 실행하십시오", "Complete and run the structured assessment"),
            L("제품·노출, AI Model Card, NAM Assay Card와 보조근거를 확인한 뒤 평가를 실행하십시오.", "Confirm the product/exposure context, AI Model Card, NAM Assay Card, and supporting evidence before running the assessment."),
            "assessment",
        )
    return (
        L("결과와 Data Gap을 검토하십시오", "Review the result and Data Gaps"),
        L("Evidence Role만 보지 말고 Hard Gate, 잔여 불확실성, 근거 추적성과 다음 확보자료를 함께 검토하십시오.", "Review the Hard Gates, residual uncertainty, evidence traceability, and next evidence—not only the Evidence Role."),
        "results",
    )


def page_consulting_studio() -> None:
    lang = language()
    render_page_header(
        L("ADVISORY STUDIO", "ADVISORY STUDIO"),
        T("consulting_studio_title"),
        T("consulting_studio_caption"),
    )
    render_section_band(
        L("고객은 서로 다른 결정을 위해 NORA를 사용합니다", "Clients use NORA for different decisions"),
        L(
            "후보선정, CRO 프로토콜 검토, 동물시험 축소, License-in 실사, Pre-IND 준비 등 목적에 따라 필요한 질문과 산출물이 달라집니다.",
            "Candidate selection, CRO protocol review, animal-study reduction, license-in diligence, and pre-IND preparation require different questions and deliverables.",
        ),
        L(f"{len(CONSULTING_CASES)}개 검증 사례", f"{len(CONSULTING_CASES)} validated cases"),
    )

    search_term = st.text_input(
        L("사례·물질·질문 검색", "Search cases, assets, or decision questions"),
        placeholder=L("예: Tacrolimus, Tirzepatide, Survivin, License-in", "e.g., Tacrolimus, Tirzepatide, survivin, license-in"),
        key=f"studio_search_{lang}",
    ).strip().lower()

    f1, f2, f3, f4 = st.columns(4)
    segment_options = ["__all__"] + sorted({case.customer_segment(lang) for case in CONSULTING_CASES.values()})
    selected_segment = f1.selectbox(
        L("고객 유형", "Customer Segment"),
        segment_options,
        format_func=lambda value: L("전체 고객", "All Clients") if value == "__all__" else value,
        key=f"studio_segment_{lang}",
    )
    objective_options = ["__all__"] + sorted({case.primary_objective(lang) for case in CONSULTING_CASES.values()})
    selected_objective = f2.selectbox(
        L("고객 목적", "Client Objective"),
        objective_options,
        format_func=lambda value: L("전체 목적", "All Objectives") if value == "__all__" else value,
        key=f"studio_objective_{lang}",
    )
    asset_options = ["__all__"] + sorted({case.asset(lang) for case in CONSULTING_CASES.values() if case.asset(lang)})
    selected_asset = f3.selectbox(
        L("대표 물질·자산", "Flagship Asset"),
        asset_options,
        format_func=lambda value: L("전체 물질", "All Assets") if value == "__all__" else value,
        key=f"studio_asset_{lang}",
    )
    scope_options = ["__all__", "engine", "expert"]
    selected_scope = f4.selectbox(
        L("자문 범위", "Advisory Scope"),
        scope_options,
        format_func=lambda value: {
            "__all__": L("전체", "All"),
            "engine": L("현재 엔진 지원", "Engine-supported"),
            "expert": L("전문가 주도", "Expert-led"),
        }[value],
        key=f"studio_scope_{lang}",
    )

    filtered_cases = []
    for case in CONSULTING_CASES.values():
        searchable = " ".join(
            [
                case.case_id, case.title(lang), case.customer_segment(lang),
                case.primary_objective(lang), case.decision_question(lang),
                case.asset(lang), case.trigger(lang), case.case_basis(lang),
            ]
        ).lower()
        if selected_segment != "__all__" and case.customer_segment(lang) != selected_segment:
            continue
        if selected_objective != "__all__" and case.primary_objective(lang) != selected_objective:
            continue
        if selected_asset != "__all__" and case.asset(lang) != selected_asset:
            continue
        if selected_scope == "engine" and not case.is_engine_supported:
            continue
        if selected_scope == "expert" and case.is_engine_supported:
            continue
        if search_term and search_term not in searchable:
            continue
        filtered_cases.append(case)
    if not filtered_cases:
        st.info(L("현재 필터에 해당하는 사례가 없습니다.", "No cases match the current filters."))
        return

    case_id = st.selectbox(
        L("사례 선택", "Select Case"),
        [case.case_id for case in filtered_cases],
        format_func=lambda value: f"{value} · {CONSULTING_CASES[value].title(lang)}",
        key=f"studio_case_{lang}",
    )
    case = CONSULTING_CASES[case_id]
    render_consulting_case_card(
        case_id=case.case_id,
        title=case.title(lang),
        segment=case.customer_segment(lang),
        objective=case.primary_objective(lang),
        engagement=case.engagement_type(lang),
        decision_question=case.decision_question(lang),
        automation_scope=case.automation_scope(lang),
    )

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric(L("대표 물질", "Asset"), case.asset(lang) or L("일반 사례", "General"))
    m2.metric(L("서비스 단계", "Service Tier"), case.service_tier(lang))
    m3.metric(L("자동화", "Automation"), L("엔진 지원", "Engine-supported") if case.is_engine_supported else L("전문가 주도", "Expert-led"))
    m4.metric(L("관련 근거", "Source Anchors"), len(case.regulatory_anchors))
    role_text = (
        f"R{case.expected_role_min}–R{case.expected_role_max}"
        if case.expected_role_min is not None and case.expected_role_max is not None
        else L("전문가 판단", "Expert judgment")
    )
    m5.metric(L("예상 근거 역할", "Expected Evidence Role"), role_text)

    cards = [
        render_advisory_card(
            T("case_deliverables"),
            case.engagement_type(lang),
            case.commercial_model(lang),
            case.deliverables(lang),
        ),
        render_advisory_card(
            T("case_actions"),
            L("다음 의사결정 단계", "Next Decision Step"),
            case.development_concern(lang),
            case.recommended_actions(lang),
        ),
    ]
    st.markdown(f'<div class="nora-advisory-grid">{"".join(cards)}</div>', unsafe_allow_html=True)

    if case.public_evidence(lang) or case.synthetic_assumptions(lang) or case.advisory_inferences(lang):
        render_section_band(
            L("근거·가정·Advisor 추론 분리", "Separate evidence, assumptions, and advisor inference"),
            case.case_basis(lang) or L("공개자료와 합성 고객상황을 구분합니다.", "Public evidence is separated from the synthetic client context."),
            case.asset(lang) or case.case_id,
        )
        evidence_cards = [
            render_advisory_card(
                L("공개자료에서 확인된 사실", "Public-source evidence"),
                case.asset(lang) or case.case_id,
                L("출처가 확인된 사실만 포함", "Only source-supported facts"),
                case.public_evidence(lang) or (L("등록된 자산별 공개근거 없음", "No asset-specific public evidence registered"),),
            ),
            render_advisory_card(
                L("가상 고객 가정", "Synthetic client assumptions"),
                L("Case-study context", "Case-study context"),
                L("실제 고객자료로 오해하지 않음", "Not presented as actual client data"),
                case.synthetic_assumptions(lang) or (L("컨설팅 방법 검증용 합성 상황", "Synthetic context for consulting-method validation"),),
            ),
            render_advisory_card(
                L("NORA의 해석·추론", "NORA advisory inferences"),
                L("의사결정 해석", "Decision interpretation"),
                L("근거와 가정에서 도출된 자문", "Advisory derived from evidence and assumptions"),
                case.advisory_inferences(lang) or (L("사례별 Advisor 추론 미등록", "No case-specific inference registered"),),
            ),
        ]
        st.markdown(f'<div class="nora-advisory-grid nora-advisory-grid-three">{"".join(evidence_cards)}</div>', unsafe_allow_html=True)

    if case.regulatory_anchors:
        registry = consulting_reference_registry()
        with st.expander(L("규제·과학 근거", "Regulatory & Scientific Anchors"), expanded=False):
            for anchor in case.regulatory_anchors:
                ref = registry.get(anchor, {})
                title = ref.get("title", anchor)
                status = ref.get("status", "")
                source_type = ref.get("source_type", "")
                url = ref.get("url", "")
                limitations = ref.get("limitations", "")
                if url:
                    st.markdown(f"- **{anchor}** — [{title}]({url})")
                else:
                    st.markdown(f"- **{anchor}** — {title}")
                detail = " · ".join(item for item in [source_type, status] if item)
                if detail:
                    st.caption(detail)
                if limitations:
                    st.caption(L("사용 한계: ", "Limitation: ") + limitations)

    if case.is_engine_supported:
        if st.button(L("이 사례로 프로젝트 시작", "Start a Project from This Case"), type="primary", use_container_width=True, key=f"studio_load_{case.case_id}"):
            demo_project = ProjectBundle.new(name=f"{case.case_id} · {case.title(lang)}")
            demo_project.description = f"{case.customer_segment(lang)} | {case.primary_objective(lang)} | {case.engagement_type(lang)}"
            demo_project.assessment_input = load_consulting_assessment(case.case_id)
            demo_project.add_event("컨설팅 사례 불러오기", case.case_id)
            set_project(demo_project, "assessment")
            st.rerun()
    else:
        st.warning(L(
            "이 사례는 현재 EarlyTox 자동화 범위를 넘어섭니다. NORA는 근거구조와 질문을 정리하지만 최종 자문은 전문가 주도로 수행해야 합니다.",
            "This case extends beyond the current EarlyTox automation scope. NORA can structure the evidence and questions, but the final advisory must remain expert-led.",
        ))

    with st.expander(T("case_library_table"), expanded=False):
        rows = [
            {
                "Case ID": item.case_id,
                L("대표 물질", "Asset"): item.asset(lang) or L("일반", "General"),
                L("고객 유형", "Client Segment"): item.customer_segment(lang),
                L("고객 목적", "Client Objective"): item.primary_objective(lang),
                L("사례", "Case"): item.title(lang),
                L("사례 성격", "Case Basis"): item.case_basis(lang),
                L("자문 범위", "Advisory Scope"): item.automation_scope(lang),
            }
            for item in filtered_cases
        ]
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

def page_project_overview() -> None:
    p = project()
    render_page_header(
        L("01 · 프로젝트 개요", "01 · Project overview"),
        T("project_overview"),
        T("overview_text"),
    )

    cou = p.assessment_input.context_of_use
    product = p.assessment_input.product
    current = result()
    next_title, next_description, next_page = _next_action_state()
    render_next_action(next_title, next_description, T("next_best_action"))
    if st.button(L("권장 작업으로 이동", "Go to Recommended Workspace"), type="primary", key=f"next_action_{p.project_id}"):
        _queue_navigation(next_page)
        st.rerun()

    left, right = st.columns([1.18, 0.82], gap="large")
    with left:
        qoi = cou.question_of_interest or T("qoi_missing")
        st.markdown(
            f"""
<div class="nora-decision-card">
  <div class="nora-card-label">{safe_html(T('current_question'))}</div>
  <h3>{safe_html(qoi)}</h3>
  <div class="nora-tag-row">
    <span class="nora-tag">{safe_html(T('assessment_objective'))} · {safe_html(fmt(cou.objective))}</span>
    <span class="nora-tag">{safe_html(T('development_stage'))} · {safe_html(fmt(cou.development_stage))}</span>
    <span class="nora-tag">Endpoint · {safe_html(fmt(cou.target_endpoint))}</span>
    <span class="nora-tag">{safe_html(T('intended_role'))} · {safe_html(fmt(cou.intended_evidence_role))}</span>
  </div>
</div>
<div class="nora-context-grid">
  <div class="nora-context-card"><span>{safe_html(T('candidate'))}</span><strong>{safe_html(product.product_name or T('not_entered'))}</strong><small>{safe_html(fmt(product.modality))}</small></div>
  <div class="nora-context-card"><span>{safe_html(T('target_mechanism'))}</span><strong>{safe_html(product.target_mechanism or T('not_entered'))}</strong><small>{safe_html(fmt(cou.target_endpoint))}</small></div>
  <div class="nora-context-card"><span>{safe_html(T('carrier_formulation'))}</span><strong>{safe_html(product.carrier_formulation or T('not_entered'))}</strong><small>{safe_html(fmt(product.route))}</small></div>
  <div class="nora-context-card"><span>{safe_html(T('route_exposure'))}</span><strong>{safe_html(fmt(product.route))}</strong><small>{safe_html(fmt(product.exposure_pattern))}</small></div>
</div>
""",
            unsafe_allow_html=True,
        )

    with right:
        role_rows = [role_definition(role, language()) for role in range(6)]
        render_role_ladder(
            role_rows,
            current_role=current.evidence_role if current else None,
            heading=T("judgments_made"),
        )

    render_section_band(
        T("quick_start"),
        L("현재 목적에 맞는 작업공간으로 바로 이동할 수 있습니다.", "Move directly to the workspace that matches the current decision need."),
        L("4개 시작점", "4 entry points"),
    )
    st.markdown(
        f"""
<div class="nora-task-grid">
  <div class="nora-task-card"><div class="nora-task-index">01 · EVIDENCE</div><strong>{safe_html(T('start_upload'))}</strong><span>{safe_html(L('AI 모델 카드, NAM 보고서, PK/TK 자료를 출처 위치와 함께 구조화합니다.', 'Structure AI model cards, NAM reports, and PK/TK evidence with source locations.'))}</span></div>
  <div class="nora-task-card"><div class="nora-task-index">02 · ASSESSMENT</div><strong>{safe_html(T('start_manual'))}</strong><span>{safe_html(L('Context of Use와 제품·노출 맥락을 직접 정의해 평가를 시작합니다.', 'Define the Context of Use and product/exposure context to start an assessment.'))}</span></div>
  <div class="nora-task-card"><div class="nora-task-index">03 · ADVISORY</div><strong>{safe_html(_page('consulting'))}</strong><span>{safe_html(L('고객 유형과 개발목적에 맞는 사례, 산출물, 자동화 범위를 비교합니다.', 'Compare client-specific cases, deliverables, and automation boundaries.'))}</span></div>
  <div class="nora-task-card"><div class="nora-task-index">04 · DEMO</div><strong>{safe_html(T('gplct_case'))}</strong><span>{safe_html(L('적용범위 밖 음성예측과 데이터 갭이 어떻게 제한되는지 확인합니다.', 'See how out-of-domain negative predictions and data gaps limit evidence use.'))}</span></div>
</div>
""",
        unsafe_allow_html=True,
    )
    q1, q2, q3, q4 = st.columns(4)
    if q1.button(T("start_upload"), use_container_width=True, key=f"quick_upload_{p.project_id}"):
        _queue_navigation("documents")
        st.rerun()
    if q2.button(T("start_manual"), use_container_width=True, key=f"quick_manual_{p.project_id}"):
        _queue_navigation("assessment")
        st.rerun()
    if q3.button(_page("consulting"), use_container_width=True, key=f"quick_consulting_{p.project_id}"):
        _queue_navigation("consulting")
        st.rerun()
    if q4.button(T("gplct_case"), use_container_width=True, key=f"quick_gplct_{p.project_id}"):
        demo_project = ProjectBundle.new(name="GP-L-CT EarlyTox")
        demo_project.assessment_input = load_case("GP-L-CT — 적용범위 밖 음성예측", language())
        set_project(demo_project, "assessment")
        st.rerun()

    st.markdown(
        f'<div class="nora-compact-note"><strong>{safe_html(T("judgments_not_made"))}</strong><br>{safe_html(T("not_decide_text"))}</div>',
        unsafe_allow_html=True,
    )

def _process_files(uploaded_files: list[Any]) -> tuple[int, int]:
    p = project()
    existing_hashes = {item.sha256 for item in p.documents}
    added_documents: list[DocumentRecord] = []
    skipped = 0
    for uploaded in uploaded_files:
        data = uploaded.getvalue()
        record = extract_document(data, uploaded.name, uploaded.type)
        if record.sha256 in existing_hashes:
            skipped += 1
            continue
        p.documents.append(record)
        added_documents.append(record)
        existing_hashes.add(record.sha256)
    if added_documents:
        new_assertions = extract_assertions_from_documents(added_documents)
        p.assertions.extend(new_assertions)
        add_event("문서 및 Assertion 추가", f"문서 {len(added_documents)}개, Assertion {len(new_assertions)}개")
        invalidate_result()
    return len(added_documents), skipped


def page_documents() -> None:
    p = project()
    render_page_header(
        L("02 · 문서 근거", "02 · Document evidence"),
        T("document_workspace"),
        T("document_workspace_caption"),
    )
    render_section_band(
        L("문서가 곧 결론은 아닙니다", "A document is not yet a conclusion"),
        L(
            "NORA는 문서에서 출처가 연결된 Assertion 후보를 만들고, 사람이 검토한 값만 평가 입력에 반영합니다.",
            "NORA creates source-linked candidate Assertions from documents and uses only human-reviewed values in the assessment.",
        ),
        "PDF · DOCX · XLSX · CSV · TXT · JSON",
    )

    upload_col, paste_col = st.columns([1.1, .9], gap="large")
    with upload_col:
        st.markdown(f"#### {L('파일 업로드', 'Upload Files')}")
        upload = st.file_uploader(
            T("document_uploader"),
            type=["pdf", "docx", "txt", "md", "csv", "xlsx", "xlsm", "json"],
            accept_multiple_files=True,
            key=f"doc_upload_{p.project_id}",
        )
        st.caption(L(
            "검색 가능한 PDF를 사용하십시오. 스캔 PDF는 현재 OCR하지 않으며, 원문 페이지·문단·시트 위치를 보존합니다.",
            "Use searchable PDFs. Scanned PDFs are not OCR-processed in this version; source page, paragraph, and sheet locations are preserved.",
        ))
        process_upload = st.button(
            T("process_documents"),
            type="primary",
            use_container_width=True,
            disabled=not bool(upload),
            key=f"process_docs_{p.project_id}",
        )
    with paste_col:
        st.markdown(f"#### {L('텍스트 직접 입력', 'Paste Evidence Text')}")
        manual = st.text_area(
            T("manual_evidence"),
            height=170,
            key=f"manual_evidence_{p.project_id}",
            placeholder=T("manual_evidence_placeholder"),
            label_visibility="collapsed",
        )
        st.caption(L(
            "짧은 모델 검증요약이나 회의 메모에 사용하십시오. 고영향 결론에는 원본 문서와 출처 위치가 필요합니다.",
            "Use this for short model summaries or meeting notes. High-impact conclusions still require original, source-located evidence.",
        ))
        process_manual = st.button(
            T("add_pasted_text"),
            use_container_width=True,
            disabled=not manual.strip(),
            key=f"add_manual_{p.project_id}",
        )

    if process_upload:
        with st.spinner(T("processing_documents")):
            added, skipped = _process_files(upload or [])
        st.success(T("documents_added", added=added, skipped=skipped))
        st.rerun()
    if process_manual:
        class ManualFile:
            name = "Manual_Evidence.txt"
            type = "text/plain"
            def getvalue(self_inner):
                return manual.encode("utf-8")
        added, _skipped = _process_files([ManualFile()])
        st.success(T("manual_added", added=added))
        st.rerun()

    if not p.documents:
        st.info(T("no_documents"))
        return

    render_section_band(
        T("document_inventory"),
        L("문서 처리상태와 Assertion 수를 확인한 뒤, 원문 구간을 검토하십시오.", "Review processing status and Assertion counts, then inspect the original evidence segment."),
        T("items_count", count=len(p.documents)),
    )
    inventory_rows = [localize_document_row(document_inventory_row(item), language()) for item in p.documents]
    st.dataframe(pd.DataFrame(inventory_rows), hide_index=True, use_container_width=True, height=min(420, 90 + 36 * len(inventory_rows)))

    selected_name = st.selectbox(T("review_document"), [item.name for item in p.documents], key=f"selected_doc_{p.project_id}")
    selected = next(item for item in p.documents if item.name == selected_name)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(T("evidence_segments"), len(selected.segments))
    m2.metric(T("characters_extracted"), f"{len(selected.extracted_text):,}")
    m3.metric(T("auto_assertions"), sum(1 for item in p.assertions if item.source_document_id == selected.document_id))
    m4.metric(T("warnings"), len(selected.warnings))

    if selected.warnings:
        with st.expander(T("document_warnings"), expanded=True):
            for warning in selected.warnings:
                st.warning(warning)

    if selected.segments:
        location = st.selectbox(T("source_location"), [segment.location for segment in selected.segments], key=f"segment_{selected.document_id}")
        segment = next(item for item in selected.segments if item.location == location)
        st.text_area(T("extracted_text"), segment.text, height=360, disabled=True, key=f"segment_text_{selected.document_id}_{location}")

    d1, d2 = st.columns([1, 3])
    if d1.button(T("delete_document"), use_container_width=True, key=f"delete_doc_{selected.document_id}"):
        p.documents = [item for item in p.documents if item.document_id != selected.document_id]
        p.assertions = [item for item in p.assertions if item.source_document_id != selected.document_id]
        add_event("문서 삭제", selected.name)
        invalidate_result()
        st.rerun()
    d2.caption(T("delete_doc_note"))

def page_assertion_review() -> None:
    p = project()
    lang = language()
    render_page_header(
        L("03 · 사람 검토", "03 · Human evidence review"),
        T("assertion_review"),
        T("assertion_review_caption"),
    )

    if not p.assertions:
        st.info(T("no_assertions"))
        return

    counts = _status_counts()
    reviewed_count = counts.get("승인", 0) + counts.get("수정", 0) + counts.get("거절", 0)
    review_percent = int(round(reviewed_count / max(1, len(p.assertions)) * 100))
    render_section_band(
        L("검토 진행상태", "Review Progress"),
        L(
            "자동 추출값은 모두 후보입니다. 특히 ‘없음’, ‘미포함’, ‘측정하지 않음’과 같은 부정문은 원문 범위를 직접 확인하십시오.",
            "All extracted values are candidates. Verify the source scope directly, especially for negations such as not available, not included, or not measured.",
        ),
        f"{review_percent}%",
    )
    st.progress(review_percent / 100)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(T("total"), len(p.assertions))
    c2.metric(T("proposed"), counts.get("제안됨", 0))
    c3.metric(T("approved_corrected"), counts.get("승인", 0) + counts.get("수정", 0))
    c4.metric(T("rejected"), counts.get("거절", 0))

    reviewed_conflicts = reviewed_assertion_conflicts(p.assertions)
    if reviewed_conflicts:
        conflict_lines = "; ".join(f"{field}: {', '.join(values)}" for field, values in reviewed_conflicts.items())
        st.error(L(
            f"상충하는 승인·수정 값이 있습니다. 자동 적용이 차단됩니다: {conflict_lines}",
            f"Conflicting approved/corrected values were found. Automatic application is blocked: {conflict_lines}",
        ))

    all_value = "__all__"
    with st.expander(L("검토 필터와 검색", "Review Filters & Search"), expanded=True):
        f1, f2, f3 = st.columns(3)
        categories = sorted({item.category for item in p.assertions})
        documents = sorted({item.source_document_name for item in p.assertions})
        selected_category = f1.selectbox(
            T("category"),
            [all_value] + categories,
            format_func=lambda value: T("total") if value == all_value else category_label(value, lang),
            key=f"assert_cat_{p.project_id}",
        )
        selected_status = f2.selectbox(
            T("review_status"),
            [all_value] + REVIEW_STATUS_OPTIONS,
            format_func=lambda value: T("total") if value == all_value else review_status_label(value, lang),
            key=f"assert_status_{p.project_id}",
        )
        selected_document = f3.selectbox(
            T("source_document"),
            [all_value] + documents,
            format_func=lambda value: T("total") if value == all_value else value,
            key=f"assert_doc_{p.project_id}",
        )
        search = st.text_input(T("search"), key=f"assert_search_{p.project_id}", placeholder=T("search_placeholder"))

    filtered: list[EvidenceAssertion] = []
    for item in p.assertions:
        if selected_category != all_value and item.category != selected_category:
            continue
        if selected_status != all_value and item.review_status != selected_status:
            continue
        if selected_document != all_value and item.source_document_name != selected_document:
            continue
        haystack = f"{item.label_ko} {assertion_field_label(item, 'en')} {item.proposed_value} {fmt(item.proposed_value)} {item.source_excerpt}".lower()
        if search and search.lower() not in haystack:
            continue
        filtered.append(item)

    raw_rows = assertion_table_rows(filtered)
    rows = [localize_assertion_row(row, item, lang) for row, item in zip(raw_rows, filtered)]
    if not rows:
        st.warning(T("no_filtered_assertions"))
        return

    st.caption(L(
        f"현재 필터 결과 {len(rows)}개. 값, 출처 위치, 원문 발췌를 함께 읽고 상태를 지정하십시오.",
        f"{len(rows)} Assertion(s) match the current filters. Review the value, source location, and source excerpt together before assigning a status.",
    ))
    frame = pd.DataFrame(rows)
    cols = ASSERTION_COLUMNS[lang]
    status_column = cols["검토 상태"]
    confidence_column = cols["추출 신뢰도"]
    excerpt_column = cols["근거 발췌"]
    value_column = cols["제안/수정 값"]
    note_column = cols["검토 메모"]
    disabled = [
        cols["Assertion ID"], cols["분류"], cols["평가 필드"], cols["Field Path"], cols["형식"],
        cols["출처 문서"], cols["출처 위치"], cols["근거 발췌"], cols["추출 신뢰도"],
    ]
    review_options = [review_status_label(status, lang) for status in REVIEW_STATUS_OPTIONS]
    edited = st.data_editor(
        frame,
        hide_index=True,
        use_container_width=True,
        height=540,
        num_rows="fixed",
        key=f"assertion_editor_{p.project_id}_{selected_category}_{selected_status}_{selected_document}_{lang}",
        disabled=disabled,
        column_config={
            status_column: st.column_config.SelectboxColumn(status_column, options=review_options, required=True, width="medium"),
            confidence_column: st.column_config.NumberColumn(confidence_column, min_value=0.0, max_value=1.0, format="%.2f", width="small"),
            excerpt_column: st.column_config.TextColumn(excerpt_column, width="large"),
            value_column: st.column_config.TextColumn(value_column, width="medium"),
            note_column: st.column_config.TextColumn(note_column, width="medium"),
        },
    )

    b1, b2 = st.columns([1, 1])
    if b1.button(T("save_edits"), type="primary", use_container_width=True, key=f"save_assert_{p.project_id}_{lang}"):
        internal_rows = [internalize_assertion_row(row, lang) for row in edited.to_dict("records")]
        updated_subset = assertions_from_table_rows(internal_rows, p.assertions)
        updated_by_id = {item.assertion_id: item for item in updated_subset}
        p.assertions = [updated_by_id.get(item.assertion_id, item) for item in p.assertions]
        add_event("Assertion 검토 저장", f"필터 결과 {len(updated_subset)}개")
        invalidate_result()
        st.success(T("review_saved"))
        st.rerun()
    if b2.button(
        T("apply_approved"),
        use_container_width=True,
        key=f"apply_assert_{p.project_id}_{lang}",
        disabled=bool(reviewed_conflicts),
        help=L("상충하는 reviewed value를 먼저 하나로 해결하십시오.", "Resolve conflicting reviewed values before applying them.") if reviewed_conflicts else None,
    ):
        p.assessment_input = apply_reviewed_assertions(p.assessment_input, p.assertions)
        add_event("승인 Assertion 적용", f"승인·수정 {sum(1 for item in p.assertions if item.review_status in {'승인','수정'})}개")
        invalidate_result()
        st.success(T("approved_applied"))
        _queue_navigation("assessment")
        st.rerun()

    st.info(L(
        "안전설계: 필터 결과 일괄 승인은 제공하지 않습니다. 동일 필드의 상충값과 부정문을 개별 검토한 뒤 승인 또는 수정하십시오.",
        "Safety-by-design: bulk approval is disabled. Review conflicting values and negation scope individually before approval or correction.",
    ))
    with st.expander(T("evidence_principles")):
        if lang == "ko":
            st.markdown(
                """
- `제안됨`: AI 또는 규칙기반 추출 후보이며 평가에 사용하지 않음
- `승인`: 출처와 값이 맞다고 사람이 확인
- `수정`: 사람이 값을 수정한 후 평가에 사용
- `거절`: 잘못된 추출이므로 사용하지 않음
- R4/R5에는 단순 문서 존재가 아니라 **출처 위치가 연결된 승인 Assertion과 전문가 검토**가 필요
"""
            )
        else:
            st.markdown(
                """
- `Proposed`: an AI- or rule-extracted candidate; not used in the assessment
- `Approved`: a human confirmed the source and value
- `Corrected`: a human corrected the value before use
- `Rejected`: an incorrect extraction that is excluded
- R4/R5 require **reviewed, source-linked Assertions and toxicology-expert review**, not merely the presence of a document
"""
            )

def _assessment_form() -> AssessmentInput | None:
    p = project()
    current = p.assessment_input
    prefix = p.project_id

    def idx(options: list[Any], current_value: Any) -> int:
        return options.index(current_value) if current_value in options else 0

    def sb(target: Any, label_ko: str, label_en: str, options: list[Any], current_value: Any, key: str) -> Any:
        return target.selectbox(
            L(label_ko, label_en),
            options,
            index=idx(options, current_value),
            format_func=fmt,
            key=f"{prefix}_{key}",
        )

    with st.form(f"assessment_form_{prefix}"):
        tabs = st.tabs(
            [
                "Context of Use",
                L("제품·노출", "Product & Exposure"),
                "AI Model Card",
                "NAM Assay Card",
                L("보조근거·Governance", "Supporting Evidence & Governance"),
            ]
        )

        endpoint_options = ["초기 간독성", "신독성", "심장독성", "면역독성", "유전독성"]
        with tabs[0]:
            render_section_band(
                L("결정 맥락", "Decision Context"),
                L("무엇을 결정하려는지, 잘못된 판단의 영향이 얼마나 큰지 먼저 정의합니다.", "Define the decision, the intended evidence role, and the consequence of an incorrect conclusion before reviewing model outputs."),
                "Context of Use",
            )
            c1, c2, c3 = st.columns(3)
            objective_options = ["AI 독성예측 결과 검증", "NAM 결과의 사람 관련성 평가", "AI·NAM·기존 근거 통합", "동물시험 범위 축소 가능성 평가", "특정 독성시험 대체 후보 평가"]
            objective = sb(c1, "평가 목적", "Assessment Objective", objective_options, current.context_of_use.objective, "cou_objective")
            stage_options = ["탐색 연구", "후보물질 선정", "초기 비임상 개발", "IND/CTA 준비"]
            development_stage = sb(c2, "개발 단계", "Development Stage", stage_options, current.context_of_use.development_stage, "cou_stage")
            target_endpoint = sb(c3, "대상 Endpoint", "Target Endpoint", endpoint_options, current.context_of_use.target_endpoint, "cou_endpoint")
            question = st.text_area(
                "Question of Interest",
                value=current.context_of_use.question_of_interest,
                height=110,
                key=f"{prefix}_cou_question",
                placeholder=L(
                    "예: 현재 AI와 사람 기반 NAM 근거가 후보물질의 초기 간독성을 평가하고 후속 동물시험 범위를 줄이는 데 충분한가?",
                    "Example: Are the current AI and human-relevant NAM data sufficient to assess early hepatotoxicity and support reduction of a follow-up animal study?",
                ),
            )
            r1, r2, r3 = st.columns(3)
            role_options = ["R1 · 가설 생성", "R2 · 초기 선별", "R3 · 보조 근거", "R4 · 동물시험 축소 지원", "R5 · 특정 시험 대체 후보"]
            intended_role = sb(r1, "의도한 Evidence Role", "Intended Evidence Role", role_options, current.context_of_use.intended_evidence_role, "cou_role")
            jurisdiction_options = ["연구용 / 내부 의사결정", "미국 FDA 사전미팅 준비", "유럽 EMA Scientific Advice 준비", "CTA/IND 근거 패키지 준비"]
            jurisdiction = sb(r2, "관할·규제 맥락", "Jurisdiction / Regulatory Context", jurisdiction_options, current.context_of_use.jurisdiction, "cou_jurisdiction")
            decision_owner = r3.text_input(L("의사결정 책임자", "Decision Owner"), value=current.context_of_use.decision_owner, key=f"{prefix}_cou_owner")
            risk1, risk2 = st.columns(2)
            model_influence = risk1.slider(
                L("AI/NAM 결과의 의사결정 영향", "Influence of AI/NAM on the Decision"),
                1,
                5,
                int(current.context_of_use.model_influence),
                key=f"{prefix}_cou_influence",
                help=L("1은 참고자료, 5는 사실상 단독 결정입니다.", "1 means reference-only; 5 means the output is effectively the sole determinant."),
            )
            decision_consequence = risk2.slider(
                L("오판 시 결과의 심각성", "Consequence of an Incorrect Decision"),
                1,
                5,
                int(current.context_of_use.decision_consequence),
                key=f"{prefix}_cou_consequence",
            )

        with tabs[1]:
            render_section_band(
                L("제품과 예정 노출", "Product & Intended Exposure"),
                L("제품 modality, 전달체, 경로, 반복기간과 사람노출을 함께 입력해야 AI/NAM 결과의 적용성을 판단할 수 있습니다.", "Product modality, carrier, route, duration, and human exposure must be considered together when judging AI/NAM applicability."),
                L("필수 맥락", "Required context"),
            )
            p1, p2, p3 = st.columns(3)
            product_name = p1.text_input(L("후보물질명", "Candidate Name"), value=current.product.product_name, key=f"{prefix}_product_name")
            modality_options = ["저분자 NME", "올리고뉴클레오타이드", "siRNA 치료제", "나노의약품", "siRNA + 나노의약품", "바이오의약품", "유전자치료제"]
            modality = sb(p2, "제품 Modality", "Product Modality", modality_options, current.product.modality, "product_modality")
            indication = p3.text_input(L("적응증", "Indication"), value=current.product.indication, key=f"{prefix}_product_indication")
            p4, p5, p6 = st.columns(3)
            active_substance = p4.text_input(L("유효성분·서열", "Active Substance / Sequence"), value=current.product.active_substance, key=f"{prefix}_product_active")
            target_mechanism = p5.text_input(L("표적·작용기전", "Target / Mechanism of Action"), value=current.product.target_mechanism, key=f"{prefix}_product_target")
            carrier_formulation = p6.text_input(L("전달체·제형", "Carrier / Formulation"), value=current.product.carrier_formulation, key=f"{prefix}_product_carrier")
            p7, p8, p9 = st.columns(3)
            route_options = ["경구", "정맥투여", "근육주사", "피하주사", "흡입", "국소"]
            route = sb(p7, "투여경로", "Route of Administration", route_options, current.product.route, "product_route")
            exposure_options = ["단회 노출", "반복 노출", "지속 노출"]
            exposure_pattern = sb(p8, "노출 형태", "Exposure Pattern", exposure_options, current.product.exposure_pattern, "product_exposure")
            planned_dose = p9.text_input(L("계획 용량", "Planned Dose"), value=current.product.planned_dose, key=f"{prefix}_product_dose")
            p10, p11, p12 = st.columns(3)
            frequency = p10.text_input(L("투여빈도", "Dosing Frequency"), value=current.product.frequency, key=f"{prefix}_product_frequency")
            treatment_duration = p11.text_input(L("투여기간", "Treatment Duration"), value=current.product.treatment_duration, key=f"{prefix}_product_duration")
            target_organs = p12.text_input(L("예상 표적장기", "Expected Target Organs"), value=current.product.target_organs, key=f"{prefix}_product_organs")
            p13, p14 = st.columns(2)
            human_cmax = p13.text_input(L("예상 Cmax", "Expected Cmax"), value=current.product.human_cmax, key=f"{prefix}_product_cmax")
            human_auc = p14.text_input(L("예상 AUC", "Expected AUC"), value=current.product.human_auc, key=f"{prefix}_product_auc")
            p15, p16 = st.columns(2)
            distribution_options = ["없음", "정성적 자료", "정량적 자료"]
            distribution_status = sb(p15, "Biodistribution", "Biodistribution", distribution_options, current.product.distribution_status, "product_distribution")
            rep_options = ["불명확", "부분적으로 확인", "임상제품 대표성 확인"]
            representativeness = sb(p16, "시험물질 대표성", "Test-Article Representativeness", rep_options, current.product.test_article_representativeness, "product_representative")

        with tabs[2]:
            render_section_band(
                L("AI 독성 예측의 신뢰성", "AI Toxicity Prediction Credibility"),
                L(
                    "평균 정확도나 p-value만으로 판단하지 않습니다. 데이터 출처, ground truth, leakage, calibration, applicability domain, 개별 예측 불확실성과 lifecycle을 분리해 검토합니다.",
                    "Do not rely on average accuracy or p-values alone. Review data provenance, ground truth, leakage, calibration, applicability domain, prediction-level uncertainty, and lifecycle governance separately.",
                ),
                L("AI 신뢰성 프로파일", "AI credibility profile"),
            )
            use_ai = st.checkbox(
                L("AI/in silico 근거 사용", "Use AI / In Silico Evidence"),
                value=current.ai_model.use_ai,
                key=f"{prefix}_ai_use",
            )
            st.caption(
                L(
                    "모델 출력확률은 NORA의 Evidence Confidence와 동일하지 않습니다. 필수정보가 없으면 비워두고, 근거가 있는 값만 입력하십시오.",
                    "A model output probability is not the same as NORA Evidence Confidence. Leave fields blank when evidence is unavailable and enter only source-supported values.",
                )
            )

            with st.expander(L("1 · 모델 식별과 예측 결과", "1 · Model Identity & Prediction"), expanded=True):
                a1, a2, a3 = st.columns(3)
                model_name = a1.text_input(L("모델명", "Model Name"), value=current.ai_model.model_name, key=f"{prefix}_ai_name")
                model_version = a2.text_input(L("모델 버전", "Model Version"), value=current.ai_model.model_version, key=f"{prefix}_ai_version")
                model_type_options = ["Rule-based QSAR", "Statistical QSAR", "Machine learning classifier", "Deep learning / GNN", "Transcriptomic signature model"]
                model_type = sb(a3, "모델 유형", "Model Type", model_type_options, current.ai_model.model_type, "ai_type")
                a4, a5, a6 = st.columns(3)
                ai_endpoint = sb(a4, "예측 Endpoint", "Predicted Endpoint", endpoint_options, current.ai_model.endpoint, "ai_endpoint")
                result_options = ["음성 / 낮은 위험 예측", "양성 / 위험 신호", "경계 / 불확실"]
                ai_result = sb(a5, "AI 예측 결과", "AI Prediction Result", result_options, current.ai_model.result, "ai_result")
                ai_probability = a6.text_input(
                    L("모델 출력값(%)", "Model Output (%)"),
                    value="" if current.ai_model.probability_percent is None else str(current.ai_model.probability_percent),
                    key=f"{prefix}_ai_probability",
                    help=L("확률, 원시 score 또는 ensemble agreement 중 무엇인지 다음 항목에서 정의합니다.", "Define below whether this is a probability, raw score, or ensemble agreement."),
                )
                a7, a8 = st.columns(2)
                probability_type_options = ["보정된 확률", "원시 모델점수", "Ensemble agreement", "불명확"]
                probability_type = sb(a7, "출력값의 의미", "Output Semantics", probability_type_options, current.ai_model.probability_type, "ai_probability_type")
                ai_source = a8.text_input(L("모델·검증자료 출처", "Model / Validation Source"), value=current.ai_model.source, key=f"{prefix}_ai_source")

            with st.expander(L("2 · Endpoint와 Ground Truth", "2 · Endpoint & Ground Truth"), expanded=False):
                endpoint_definition = st.text_area(
                    L("Endpoint 정의", "Endpoint Definition"),
                    value=current.ai_model.endpoint_definition,
                    height=85,
                    key=f"{prefix}_ai_endpoint_definition",
                    help=L("양성·음성 기준, 관찰기간, 중증도 및 adverse threshold를 구체적으로 기록합니다.", "Specify positive/negative criteria, observation window, severity, and adversity threshold."),
                )
                g1, g2 = st.columns(2)
                reference_options = ["전문가 adjudication / 임상 기준", "검증된 in vivo / 병리 기준", "검증된 NAM 기준", "문헌 / 라벨 기반", "불명확"]
                reference_standard = sb(g1, "Reference standard", "Reference Standard", reference_options, current.ai_model.reference_standard, "ai_reference_standard")
                label_quality_options = ["전문가 검토·합의", "독립적 검토", "단일 출처 / 자동 라벨", "불명확"]
                label_quality = sb(g2, "Label 품질", "Label Quality", label_quality_options, current.ai_model.label_quality, "ai_label_quality")
                g3, g4 = st.columns(2)
                missing_policy_options = ["미평가와 음성을 명확히 구분", "일부 구분", "미평가를 음성으로 처리", "불명확"]
                missing_label_policy = sb(g3, "Missing-label 정책", "Missing-Label Policy", missing_policy_options, current.ai_model.missing_label_policy, "ai_missing_policy")
                g4.markdown("<div style='height:.1rem'></div>", unsafe_allow_html=True)
                time_window_defined = g4.checkbox(L("독성 관찰기간이 정의됨", "Toxicity Time Window Defined"), value=current.ai_model.time_window_defined, key=f"{prefix}_ai_time_window")
                severity_threshold_defined = g4.checkbox(L("중증도·Adversity 기준이 정의됨", "Severity / Adversity Threshold Defined"), value=current.ai_model.severity_threshold_defined, key=f"{prefix}_ai_severity_threshold")

            with st.expander(L("3 · 학습데이터, 분할과 Leakage", "3 · Dataset, Splitting & Leakage"), expanded=False):
                d1, d2 = st.columns(2)
                dataset_source = d1.text_input(L("데이터 출처", "Dataset Source"), value=current.ai_model.dataset_source, key=f"{prefix}_ai_dataset_source")
                dataset_version = d2.text_input(L("데이터셋 버전·식별자", "Dataset Version / Identifier"), value=current.ai_model.dataset_version, key=f"{prefix}_ai_dataset_version")
                d3, d4 = st.columns(2)
                training_sample_size = d3.text_input(L("학습표본 수", "Training Sample Size"), value="" if current.ai_model.training_sample_size is None else str(current.ai_model.training_sample_size), key=f"{prefix}_ai_training_n")
                positive_class_percent = d4.text_input(L("독성 양성 비율(%)", "Positive Toxicity Class (%)"), value="" if current.ai_model.positive_class_percent is None else str(current.ai_model.positive_class_percent), key=f"{prefix}_ai_positive_class")
                d5, d6 = st.columns(2)
                split_options = ["외부 독립검증", "시간 분할", "Scaffold 분할", "무작위 분할", "불명확"]
                split_strategy = sb(d5, "분할전략", "Split Strategy", split_options, current.ai_model.split_strategy, "ai_split_strategy")
                independence_options = ["독립 확인", "부분 확인", "비독립 / 중복 확인", "불명확"]
                test_set_independence = sb(d6, "시험세트 독립성", "Test-Set Independence", independence_options, current.ai_model.test_set_independence, "ai_test_independence")
                d7, d8 = st.columns(2)
                leakage_options = ["평가 완료 — 문제 없음", "일부 확인", "누수 가능성", "누수 확인", "미평가"]
                leakage_assessment = sb(d7, "Data leakage 평가", "Data Leakage Assessment", leakage_options, current.ai_model.leakage_assessment, "ai_leakage")
                duplicate_options = ["평가 완료 — 문제 없음", "중복 제거 / 관리", "일부 확인", "중복 확인", "미평가"]
                duplicate_assessment = sb(d8, "중복·Scaffold overlap", "Duplicate / Scaffold Overlap", duplicate_options, current.ai_model.duplicate_assessment, "ai_duplicates")
                domain_values = ["저분자", "올리고뉴클레오타이드", "나노의약품", "바이오의약품"]
                domain_modalities = st.multiselect(
                    L("학습·검증자료 Modality", "Modalities in Training / Validation Data"),
                    domain_values,
                    default=current.ai_model.domain_modalities,
                    format_func=fmt,
                    key=f"{prefix}_ai_domain_modalities",
                )

            with st.expander(L("4 · 성능, Threshold와 Calibration", "4 · Performance, Threshold & Calibration"), expanded=False):
                p1, p2 = st.columns(2)
                ext_options = ["확인됨", "부분적으로 확인", "없음", "불명확"]
                external_validation = sb(p1, "외부 독립검증", "Independent External Validation", ext_options, current.ai_model.external_validation, "ai_external")
                represent_options = ["현재 COU에 적절", "부분적으로 적절", "부적절", "불명확"]
                external_validation_representativeness = sb(p2, "외부검증 대표성", "External-Validation Representativeness", represent_options, current.ai_model.external_validation_representativeness, "ai_external_rep")
                p3, p4, p5 = st.columns(3)
                sensitivity = p3.text_input("Sensitivity (%)", value="" if current.ai_model.sensitivity_percent is None else str(current.ai_model.sensitivity_percent), key=f"{prefix}_ai_sensitivity")
                specificity = p4.text_input("Specificity (%)", value="" if current.ai_model.specificity_percent is None else str(current.ai_model.specificity_percent), key=f"{prefix}_ai_specificity")
                fnr = p5.text_input("False-negative rate (%)", value="" if current.ai_model.false_negative_rate_percent is None else str(current.ai_model.false_negative_rate_percent), key=f"{prefix}_ai_fnr")
                p6, p7, p8 = st.columns(3)
                fpr = p6.text_input("False-positive rate (%)", value="" if current.ai_model.false_positive_rate_percent is None else str(current.ai_model.false_positive_rate_percent), key=f"{prefix}_ai_fpr")
                ppv = p7.text_input("PPV (%)", value="" if current.ai_model.ppv_percent is None else str(current.ai_model.ppv_percent), key=f"{prefix}_ai_ppv")
                npv = p8.text_input("NPV (%)", value="" if current.ai_model.npv_percent is None else str(current.ai_model.npv_percent), key=f"{prefix}_ai_npv")
                p9, p10, p11 = st.columns(3)
                balanced_accuracy = p9.text_input("Balanced accuracy (%)", value="" if current.ai_model.balanced_accuracy_percent is None else str(current.ai_model.balanced_accuracy_percent), key=f"{prefix}_ai_balanced_accuracy")
                auroc = p10.text_input("AUROC (0–1)", value="" if current.ai_model.auroc is None else str(current.ai_model.auroc), key=f"{prefix}_ai_auroc")
                auprc = p11.text_input("AUPRC (0–1)", value="" if current.ai_model.auprc is None else str(current.ai_model.auprc), key=f"{prefix}_ai_auprc")
                p12, p13 = st.columns(2)
                ci_options = ["보고됨", "부분 보고", "미보고", "불명확"]
                performance_confidence_intervals = sb(p12, "성능 신뢰구간", "Performance Confidence Intervals", ci_options, current.ai_model.performance_confidence_intervals, "ai_ci")
                decision_threshold = p13.text_input(L("Decision threshold", "Decision Threshold"), value="" if current.ai_model.decision_threshold is None else str(current.ai_model.decision_threshold), key=f"{prefix}_ai_threshold")
                p14, p15, p16, p17 = st.columns(4)
                cal_options = ["검증됨", "부분 검증", "미검증", "불명확"]
                calibration = sb(p14, "확률 Calibration", "Probability Calibration", cal_options, current.ai_model.calibration_status, "ai_calibration")
                brier_score = p15.text_input("Brier score", value="" if current.ai_model.brier_score is None else str(current.ai_model.brier_score), key=f"{prefix}_ai_brier")
                calibration_slope = p16.text_input("Calibration slope", value="" if current.ai_model.calibration_slope is None else str(current.ai_model.calibration_slope), key=f"{prefix}_ai_cal_slope")
                calibration_intercept = p17.text_input("Calibration intercept", value="" if current.ai_model.calibration_intercept is None else str(current.ai_model.calibration_intercept), key=f"{prefix}_ai_cal_intercept")
                st.caption(L("p-value는 모델 차이 검정에 참고할 수 있지만, 독성모델의 유용성은 sensitivity/FNR, predictive values, calibration, confidence intervals와 applicability를 함께 봐야 합니다.", "P-values may support model-comparison tests, but toxicity-model utility requires sensitivity/FNR, predictive values, calibration, confidence intervals, and applicability together."))

            with st.expander(L("5 · 후보 적용성과 개별 예측 불확실성", "5 · Candidate Applicability & Prediction Uncertainty"), expanded=False):
                q1, q2 = st.columns(2)
                domain_options = ["자동 평가", "In-domain", "Borderline", "Out-of-domain", "Unknown"]
                domain_status = sb(q1, "후보 Applicability Domain", "Candidate Applicability Domain", domain_options, current.ai_model.domain_status, "ai_domain_status")
                ood_options = ["정량 평가 — In-domain", "정량 평가 — Borderline", "정량 평가 — Out-of-domain", "없음", "불명확"]
                ood_detection = sb(q2, "OOD 탐지", "Out-of-Distribution Detection", ood_options, current.ai_model.ood_detection, "ai_ood")
                q3, q4 = st.columns(2)
                nearest_neighbor_similarity = q3.text_input(L("가장 가까운 유사체 유사도(%)", "Nearest-Neighbor Similarity (%)"), value="" if current.ai_model.nearest_neighbor_similarity_percent is None else str(current.ai_model.nearest_neighbor_similarity_percent), key=f"{prefix}_ai_nn_similarity")
                prediction_interval = q4.text_input(L("Prediction interval / 범위", "Prediction Interval / Range"), value=current.ai_model.prediction_interval, key=f"{prefix}_ai_prediction_interval")
                q5, q6 = st.columns(2)
                uncertainty_options = ["낮음", "중간", "높음", "불명확"]
                prediction_uncertainty = sb(q5, "개별 예측 불확실성", "Prediction-Level Uncertainty", uncertainty_options, current.ai_model.prediction_uncertainty, "ai_pred_uncertainty")
                q6.markdown("<div style='height:.1rem'></div>", unsafe_allow_html=True)
                input_quality_verified = q6.checkbox(L("입력 구조·서열·제형 품질 검증 완료", "Input Structure / Sequence / Formulation Verified"), value=current.ai_model.input_quality_verified, key=f"{prefix}_ai_input_quality")
                q7, q8 = st.columns(2)
                explainability_options = ["기전과 연결됨", "부분 연결", "없음", "불명확"]
                explainability_status = sb(q7, "예측 설명가능성", "Prediction Explainability", explainability_options, current.ai_model.explainability_status, "ai_explainability")
                plausibility_options = ["높음", "중간", "낮음", "불명확"]
                biological_plausibility = sb(q8, "생물학적 타당성", "Biological Plausibility", plausibility_options, current.ai_model.biological_plausibility, "ai_plausibility")

            with st.expander(L("6 · 재현성, 변경관리와 Lifecycle", "6 · Reproducibility, Change Control & Lifecycle"), expanded=False):
                l1, l2 = st.columns(2)
                code_commit = l1.text_input(L("Code commit / model artifact ID", "Code Commit / Model Artifact ID"), value=current.ai_model.code_commit, key=f"{prefix}_ai_code_commit")
                software_environment = l2.text_input(L("Software environment / lock", "Software Environment / Lock"), value=current.ai_model.software_environment, key=f"{prefix}_ai_environment")
                l3, l4 = st.columns(2)
                training_data_hash = l3.text_input(L("학습데이터 Hash", "Training-Data Hash"), value=current.ai_model.training_data_hash, key=f"{prefix}_ai_data_hash")
                last_validation_date = l4.text_input(L("최근 검증일", "Last Validation Date"), value=current.ai_model.last_validation_date, placeholder="YYYY-MM-DD", key=f"{prefix}_ai_validation_date")
                l5, l6, l7 = st.columns(3)
                drift_options = ["운영 중", "계획 있음", "없음"]
                drift_monitoring = sb(l5, "Drift monitoring", "Drift Monitoring", drift_options, current.ai_model.drift_monitoring, "ai_drift")
                change_options = ["정의됨", "부분 정의", "불명확"]
                change_control = sb(l6, "Change control", "Change Control", change_options, current.ai_model.change_control, "ai_change_control")
                lifecycle_options = ["정의됨", "부분 정의", "없음"]
                lifecycle_plan = sb(l7, "Lifecycle plan", "Lifecycle Plan", lifecycle_options, current.ai_model.lifecycle_plan, "ai_lifecycle")
                known_limitations = st.text_area(L("알려진 한계", "Known Limitations"), value=current.ai_model.known_limitations, height=90, key=f"{prefix}_ai_limitations")

        with tabs[3]:
            render_section_band(
                L("NAM 시험계와 실행 유효성", "NAM Test System & Execution Validity"),
                L("사람 유래 여부만으로 충분하지 않습니다. 관련 세포, 대사·면역기능, 대조군, 반복노출과 실제 세포노출을 함께 확인합니다.", "Human origin alone is insufficient. Review relevant cells, metabolic and immune competence, controls, repeat exposure, and measured cellular exposure together."),
                "Assay Card",
            )
            use_nam = st.checkbox(L("사람 관련 NAM 근거 사용", "Use Human-Relevant NAM Evidence"), value=current.nam_assay.use_nam, key=f"{prefix}_nam_use")
            n1, n2, n3 = st.columns(3)
            nam_types = ["2D 세포시험", "공배양(Coculture)", "3D 간 Spheroid", "간 Organoid", "Liver-on-chip / MPS", "Omics 기반 시험"]
            nam_type = sb(n1, "NAM 유형", "NAM Type", nam_types, current.nam_assay.nam_type, "nam_type")
            origin_options = ["사람 유래", "사람·동물 혼합", "동물 유래", "불명확"]
            system_origin = sb(n2, "시험계 기원", "Test-System Origin", origin_options, current.nam_assay.system_origin, "nam_origin")
            nam_result_options = ["음성", "양성", "경계", "시험 무효"]
            nam_result = sb(n3, "NAM 결과", "NAM Result", nam_result_options, current.nam_assay.result, "nam_result")
            cell_values = ["간세포(Hepatocyte)", "Kupffer cell", "Stellate cell", "간 내피세포", "담관세포"]
            cell_types = st.multiselect(L("포함 세포", "Included Cell Types"), cell_values, default=current.nam_assay.cell_types, format_func=fmt, key=f"{prefix}_nam_cells")
            n4, n5, n6 = st.columns(3)
            metabolic_options = ["충분히 확인", "부분 확인", "확인되지 않음"]
            metabolic = sb(n4, "대사능", "Metabolic Competence", metabolic_options, current.nam_assay.metabolic_competence, "nam_metabolic")
            immune_options = ["충분", "부분적", "미포함 / 불명확"]
            immune = sb(n5, "면역반응 재현성", "Immune Competence", immune_options, current.nam_assay.immune_competence, "nam_immune")
            nam_exposure_options = ["단회/급성 노출", "반복노출", "지속노출"]
            nam_exposure = sb(n6, "NAM 노출설계", "NAM Exposure Design", nam_exposure_options, current.nam_assay.exposure_design, "nam_exposure")
            n7, n8 = st.columns(2)
            control_options = ["유효", "실패", "없음 / 불명확"]
            positive_control = sb(n7, "양성대조군", "Positive Control", control_options, current.nam_assay.positive_control, "nam_positive")
            negative_control = sb(n8, "음성대조군", "Negative Control", control_options, current.nam_assay.negative_control, "nam_negative")
            n9, n10 = st.columns(2)
            carrier_options = ["포함", "미포함", "해당 없음"]
            carrier_control = sb(n9, "Carrier-only", "Carrier-Only Control", carrier_options, current.nam_assay.carrier_only_control, "nam_carrier_control")
            active_control = sb(n10, "Active-only", "Active-Only Control", carrier_options, current.nam_assay.active_only_control, "nam_active_control")
            n11, n12 = st.columns(2)
            protocol_options = ["완결", "부분적", "불충분"]
            protocol = sb(n11, "프로토콜 완결성", "Protocol Completeness", protocol_options, current.nam_assay.protocol_completeness, "nam_protocol")
            measured_options = ["측정됨", "부분 측정", "측정 안 됨"]
            measured = sb(n12, "Free/세포내 노출", "Free / Intracellular Exposure", measured_options, current.nam_assay.measured_exposure, "nam_measured")
            n13, n14 = st.columns(2)
            qivive_options = ["수행됨", "초기 연결", "없음"]
            qivive = sb(n13, "QIVIVE/PBPK", "QIVIVE / PBPK", qivive_options, current.nam_assay.qivive_pbpk, "nam_qivive")
            repro_options = ["Donor/lot/반복 재현성 확인", "일부 확인", "확인되지 않음"]
            reproducibility = sb(n14, "재현성", "Reproducibility", repro_options, current.nam_assay.reproducibility, "nam_repro")
            nominal_exposure = st.text_input(L("명목 농도", "Nominal Concentration"), value=current.nam_assay.nominal_exposure, key=f"{prefix}_nam_nominal")
            endpoint_values = ["Cell viability / ATP", "미토콘드리아 기능", "산화스트레스", "ALT / AST / GLDH", "Cytokine", "담즙산 수송", "CYP 대사기능", "Omics signature"]
            nam_endpoints = st.multiselect("NAM Endpoint", endpoint_values, default=current.nam_assay.endpoints, format_func=fmt, key=f"{prefix}_nam_endpoints")

        with tabs[4]:
            render_section_band(
                L("독립 근거와 거버넌스", "Independent Evidence & Governance"),
                L("R4/R5와 같은 고영향 역할에는 독립 근거 흐름, 출처 추적성, Assertion 검토와 독성전문가 승인이 필요합니다.", "High-impact roles such as R4/R5 require independent evidence streams, source traceability, reviewed Assertions, and toxicology-expert approval."),
                "Human-in-the-loop",
            )
            e1, e2, e3 = st.columns(3)
            mechanistic = e1.checkbox(L("기전 기반 근거", "Mechanistic Evidence"), value=current.supporting_evidence.mechanistic_evidence, key=f"{prefix}_ev_mechanistic")
            class_evidence = e2.checkbox(L("동일계열·임상 Class 근거", "Class / Clinical Evidence"), value=current.supporting_evidence.class_or_clinical_evidence, key=f"{prefix}_ev_class")
            quantitative_bio = e3.checkbox(L("정량적 Biodistribution", "Quantitative Biodistribution"), value=current.supporting_evidence.quantitative_biodistribution, key=f"{prefix}_ev_bio")
            e4, e5, e6 = st.columns(3)
            pk_tk = e4.checkbox(L("PK/TK 및 노출-반응", "PK/TK and Exposure-Response"), value=current.supporting_evidence.pk_tk_evidence, key=f"{prefix}_ev_pktk")
            invivo = e5.checkbox(L("기존 in vivo 독성자료", "Existing In Vivo Toxicity Evidence"), value=current.supporting_evidence.existing_in_vivo_evidence, key=f"{prefix}_ev_invivo")
            human_evidence = e6.checkbox(L("사람·임상·사람 조직 근거", "Human / Clinical / Human-Tissue Evidence"), value=current.supporting_evidence.human_evidence, key=f"{prefix}_ev_human")
            g1, g2 = st.columns(2)
            traceable = g1.checkbox(L("근거 추적 가능", "Evidence Traceable"), value=current.supporting_evidence.evidence_traceable, key=f"{prefix}_gov_trace")
            assertions_reviewed = g2.checkbox(L("Assertion 검토 완료", "Assertions Reviewed"), value=current.supporting_evidence.assertions_reviewed, key=f"{prefix}_gov_assert")
            g3, g4 = st.columns(2)
            expert_reviewed = g3.checkbox(L("독성전문가 검토 완료", "Toxicology Expert Review Completed"), value=current.supporting_evidence.expert_reviewed, key=f"{prefix}_gov_expert")
            version_locked = g4.checkbox(L("버전 기록 완료", "Versions Recorded"), value=current.supporting_evidence.version_locked, key=f"{prefix}_gov_version")
            expert_note = st.text_area(L("전문가 검토 메모", "Expert Review Note"), value=current.supporting_evidence.expert_review_note, height=85, key=f"{prefix}_gov_expert_note")
            support_note = st.text_area(L("보조 근거 설명", "Supporting Evidence Note"), value=current.supporting_evidence.supporting_note, height=100, key=f"{prefix}_gov_support_note")

        submitted = st.form_submit_button(T("save_assessment_input"), type="primary", use_container_width=True)

    if not submitted:
        return None

    return AssessmentInput(
        context_of_use=ContextOfUse(
            objective=objective,
            question_of_interest=question,
            development_stage=development_stage,
            target_endpoint=target_endpoint,
            intended_evidence_role=intended_role,
            jurisdiction=jurisdiction,
            model_influence=model_influence,
            decision_consequence=decision_consequence,
            decision_owner=decision_owner,
        ),
        product=ProductContext(
            product_name=product_name,
            modality=modality,
            indication=indication,
            active_substance=active_substance,
            target_mechanism=target_mechanism,
            carrier_formulation=carrier_formulation,
            route=route,
            planned_dose=planned_dose,
            exposure_pattern=exposure_pattern,
            frequency=frequency,
            treatment_duration=treatment_duration,
            target_organs=target_organs,
            human_cmax=human_cmax,
            human_auc=human_auc,
            distribution_status=distribution_status,
            test_article_representativeness=representativeness,
        ),
        ai_model=AIModelCard(
            use_ai=use_ai,
            model_name=model_name,
            model_version=model_version,
            model_type=model_type,
            endpoint=ai_endpoint,
            result=ai_result,
            probability_percent=_optional_float(ai_probability),
            probability_type=probability_type,
            endpoint_definition=endpoint_definition,
            reference_standard=reference_standard,
            label_quality=label_quality,
            missing_label_policy=missing_label_policy,
            time_window_defined=time_window_defined,
            severity_threshold_defined=severity_threshold_defined,
            dataset_source=dataset_source,
            dataset_version=dataset_version,
            training_sample_size=_optional_int(training_sample_size),
            positive_class_percent=_optional_float(positive_class_percent),
            split_strategy=split_strategy,
            test_set_independence=test_set_independence,
            leakage_assessment=leakage_assessment,
            duplicate_assessment=duplicate_assessment,
            external_validation=external_validation,
            external_validation_representativeness=external_validation_representativeness,
            sensitivity_percent=_optional_float(sensitivity),
            specificity_percent=_optional_float(specificity),
            false_negative_rate_percent=_optional_float(fnr),
            false_positive_rate_percent=_optional_float(fpr),
            ppv_percent=_optional_float(ppv),
            npv_percent=_optional_float(npv),
            balanced_accuracy_percent=_optional_float(balanced_accuracy),
            auroc=_optional_number(auroc, 0.0, 1.0),
            auprc=_optional_number(auprc, 0.0, 1.0),
            performance_confidence_intervals=performance_confidence_intervals,
            decision_threshold=_optional_number(decision_threshold),
            calibration_status=calibration,
            brier_score=_optional_number(brier_score, 0.0, 1.0),
            calibration_slope=_optional_number(calibration_slope),
            calibration_intercept=_optional_number(calibration_intercept),
            domain_modalities=domain_modalities,
            domain_status=domain_status,
            nearest_neighbor_similarity_percent=_optional_float(nearest_neighbor_similarity),
            ood_detection=ood_detection,
            prediction_interval=prediction_interval,
            prediction_uncertainty=prediction_uncertainty,
            input_quality_verified=input_quality_verified,
            explainability_status=explainability_status,
            biological_plausibility=biological_plausibility,
            source=ai_source,
            known_limitations=known_limitations,
            code_commit=code_commit,
            software_environment=software_environment,
            training_data_hash=training_data_hash,
            last_validation_date=last_validation_date,
            drift_monitoring=drift_monitoring,
            change_control=change_control,
            lifecycle_plan=lifecycle_plan,
        ),
        nam_assay=NAMAssayCard(
            use_nam=use_nam,
            nam_type=nam_type,
            system_origin=system_origin,
            result=nam_result,
            cell_types=cell_types,
            metabolic_competence=metabolic,
            immune_competence=immune,
            exposure_design=nam_exposure,
            positive_control=positive_control,
            negative_control=negative_control,
            carrier_only_control=carrier_control,
            active_only_control=active_control,
            protocol_completeness=protocol,
            nominal_exposure=nominal_exposure,
            measured_exposure=measured,
            qivive_pbpk=qivive,
            reproducibility=reproducibility,
            endpoints=nam_endpoints,
        ),
        supporting_evidence=SupportingEvidence(
            mechanistic_evidence=mechanistic,
            class_or_clinical_evidence=class_evidence,
            quantitative_biodistribution=quantitative_bio,
            pk_tk_evidence=pk_tk,
            existing_in_vivo_evidence=invivo,
            human_evidence=human_evidence,
            evidence_traceable=traceable,
            assertions_reviewed=assertions_reviewed,
            expert_reviewed=expert_reviewed,
            version_locked=version_locked,
            expert_review_note=expert_note,
            supporting_note=support_note,
        ),
    )


def page_assessment_input() -> None:
    render_page_header(
        L("04 · 구조화 평가", "04 · Structured assessment"),
        T("structured_input"),
        T("structured_input_caption"),
    )
    updated = _assessment_form()
    if updated:
        project().assessment_input = updated
        project().touch()
        add_event("구조화 평가 입력 저장", updated.product.product_name or "후보 미입력")
        invalidate_result()
        st.success(T("assessment_saved"))
        st.rerun()


def _score_card(label: str, value: Any) -> None:
    if isinstance(value, (float, int)):
        numeric = max(0.0, min(4.0, float(value)))
        percent = numeric / 4.0 * 100.0
        value_text = f"{numeric:.1f} / 4"
    else:
        percent = 50.0
        value_text = str(value)
    st.markdown(
        f'<div class="nora-score-card"><span>{safe_html(label)}</span><strong>{safe_html(value_text)}</strong>'
        f'<div class="nora-score-track"><i style="width:{percent:.1f}%"></i></div></div>',
        unsafe_allow_html=True,
    )


def _run_assessment() -> None:
    p = project()
    assessed = evaluate(p.assessment_input)
    st.session_state.assessment_result = assessed
    p.last_result = assessed.to_dict()
    add_event("EarlyTox 평가 실행", f"{assessed.evidence_role_code} - {assessed.evidence_role_name}")


def page_results() -> None:
    p = project()
    lang = language()
    render_page_header(
        L("05 · 자문 결과", "05 · Advisory assessment"),
        T("results_title"),
        T("results_caption"),
    )

    if st.button(T("run_assessment"), type="primary", use_container_width=True, key=f"run_assessment_{p.project_id}"):
        _run_assessment()
        st.rerun()

    assessed = result()
    if not assessed:
        st.info(T("assessment_placeholder"))
        return

    localized = localize_result(assessed, p.assessment_input, lang)
    tone = role_tone(assessed.evidence_role)
    left, right = st.columns([1.18, 0.82], gap="large")
    with left:
        st.markdown(
            f"""
<div class="nora-result-card {tone['class']}">
  <div class="nora-result-label">{safe_html(T('current_role'))}</div>
  <div class="nora-result-code">{safe_html(localized['evidence_role_code'])}</div>
  <div class="nora-result-name">{safe_html(localized['evidence_role_name'])}</div>
  <div class="nora-result-desc">{safe_html(localized['evidence_role_description'])}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with right:
        status_class = "low" if assessed.evidence_role <= 2 else "mid" if assessed.evidence_role == 3 else "high"
        st.markdown(
            f"""
<div class="nora-recommendation-card">
  <h3>{safe_html(T('animal_recommendation'))}</h3>
  <div class="nora-advisory-status {status_class}">{safe_html(localized['animal_use_status'])}</div>
  <p>{safe_html(localized['animal_use_description'])}</p>
  <div class="nora-mini-metrics">
    <div class="nora-mini-metric"><span>{safe_html(T('model_risk'))}</span><strong>{safe_html(localized['model_risk'])}</strong></div>
    <div class="nora-mini-metric"><span>{safe_html(T('residual_uncertainty'))}</span><strong>{safe_html(localized['residual_uncertainty'])}</strong></div>
    <div class="nora-mini-metric"><span>{safe_html(T('independent_streams'))}</span><strong>{safe_html(localized['evidence_stream_count'])}</strong></div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div class="nora-compact-note"><strong>{safe_html(L("해석 원칙", "Interpretation principle"))}</strong><br>'
        f'{safe_html(L("Evidence Role은 근거의 사용 가능 범위이며 제품 안전성 등급이 아닙니다. 양성 독성신호가 신뢰할 수 있을수록 Evidence Role이 높을 수도 있습니다.", "Evidence Role describes the usable scope of evidence, not product safety. A credible positive toxicity signal may still have a high Evidence Role."))}</div>',
        unsafe_allow_html=True,
    )

    render_kpi_strip(
        [
            {
                "label": L("근거 신뢰도", "Evidence Confidence"),
                "value": localized["evidence_confidence"],
                "sub": L("근거 전체의 품질·적용성", "Overall evidence quality and applicability"),
                "accent": "accent-teal",
            },
            {
                "label": L("개별 AI 예측 신뢰성", "Prediction Reliability"),
                "value": localized["prediction_reliability"],
                "sub": L("현재 후보에 대한 예측 수준", "Reliability for this candidate"),
                "accent": "accent-blue",
            },
            {
                "label": L("독성 신호 방향", "Toxicity Direction"),
                "value": localized["toxicity_direction"],
                "sub": L("음성·양성·상충·미정", "Negative, positive, conflicting, or unknown"),
                "accent": "accent-amber" if assessed.toxicity_direction in {"일관된 양성 신호", "양성 신호", "상충 신호"} else "accent-blue",
            },
            {
                "label": L("개발 우려", "Development Concern"),
                "value": localized["development_concern"],
                "sub": L("근거가 보여주는 개발위험", "Development risk indicated by the evidence"),
                "accent": "accent-amber",
            },
        ],
        role=assessed.evidence_role,
    )

    if p.assessment_input.ai_model.use_ai:
        render_section_band(
            L("AI 독성 신뢰성 프로파일", "AI Toxicity Credibility Profile"),
            L(
                "평균 성능과 개별 후보 예측을 분리합니다. 낮은 p-value나 높은 accuracy만으로는 높은 신뢰성을 부여하지 않습니다.",
                "Separate model-level performance from candidate-level prediction reliability. A low p-value or high accuracy alone does not establish high credibility.",
            ),
            L("6개 AI 전용 축", "6 AI-specific dimensions"),
        )
        ai_columns = st.columns(3)
        for index, (label, value) in enumerate(localized["ai_credibility_profile"].items()):
            with ai_columns[index % 3]:
                _score_card(label, value)
        st.markdown(
            f'<div class="nora-compact-note"><strong>{safe_html(L("AI 검증 경계", "AI assurance boundary"))}</strong><br>'
            f'{safe_html(L("Data leakage, 부적절한 ground truth, out-of-domain, 미보정 확률 또는 높은 prediction uncertainty는 다른 평균점수로 상쇄되지 않습니다.", "Data leakage, inadequate ground truth, out-of-domain use, uncalibrated probabilities, or high prediction uncertainty cannot be offset by other average scores."))}</div>',
            unsafe_allow_html=True,
        )

    render_section_band(
        T("assessment_dimensions"),
        L("각 축을 따로 읽고, 평균점수보다 Hard Gate와 잔여 불확실성을 우선 확인하십시오.", "Read each dimension separately; Hard Gates and residual uncertainty take priority over averages."),
        "0–4",
    )
    ai_profile_labels = set(localized["ai_credibility_profile"].keys())
    score_items = [(label, value) for label, value in localized["scores"].items() if label not in ai_profile_labels]
    columns = st.columns(3)
    for index, (label, value) in enumerate(score_items):
        with columns[index % 3]:
            _score_card(label, value)

    render_section_band(
        T("explainable_advisory"),
        L("자동점수를 문장으로 다시 확인하여 무엇이 관찰됐고 왜 중요한지 구분합니다.", "Translate the rule output back into evidence statements so the observed facts and their implications remain distinct."),
        L("4단 자문", "4-part advisory"),
    )
    advisory_cards = [
        render_advisory_card(T("observation"), T("observation"), L("입력자료에서 직접 확인된 내용", "Directly supported by the entered evidence"), localized["observations"]),
        render_advisory_card(T("interpretation"), T("interpretation"), L("근거가 의미하는 범위와 한계", "What the evidence supports—and what it does not"), localized["interpretations"]),
        render_advisory_card(T("development_relevance"), T("development_relevance"), L("현재 개발결정에 미치는 영향", "Impact on the current development decision"), localized["development_relevance"]),
        render_advisory_card(T("recommendations"), T("recommendations"), L("가장 방어 가능한 다음 단계", "Most defensible next steps"), localized["recommendations"]),
    ]
    st.markdown(f'<div class="nora-advisory-grid">{"".join(advisory_cards)}</div>', unsafe_allow_html=True)

    tabs = st.tabs(["Hard Gates", T("data_gap"), T("evidence_ledger"), T("audit_trail")])
    with tabs[0]:
        for gate in localized["gates"]:
            css = "gate-pass" if gate["status"] in {"통과", "Pass"} else "gate-cond" if gate["status"] in {"조건부", "Conditional"} else "gate-fail"
            with st.container(border=True):
                st.markdown(
                    f"<div class='{css}' style='padding:.25rem .25rem .25rem .85rem'><strong>{gate['gate']} · {gate['status']}</strong><br>{gate['rationale']}<br><span class='small-muted'>{T('impact')}: {gate['effect']}</span></div>",
                    unsafe_allow_html=True,
                )
    with tabs[1]:
        if localized["data_gaps"]:
            top_gaps = localized["data_gaps"][:4]
            gap_cards = [
                render_advisory_card(
                    f"{item['code']} · {item['criticality']}",
                    item["title"],
                    item["description"],
                    [f"{T('impact')}: {item['effect']}", item["recommendation"]],
                )
                for item in top_gaps
            ]
            st.markdown(f'<div class="nora-advisory-grid">{"".join(gap_cards)}</div>', unsafe_allow_html=True)
            if lang == "ko":
                columns_map = {"code": "Gap Code", "title": "제목", "description": "설명", "criticality": "중요도", "rule_id": "Rule ID", "effect": "판정 영향", "recommendation": "권고"}
            else:
                columns_map = {"code": "Gap Code", "title": "Title", "description": "Description", "criticality": "Criticality", "rule_id": "Rule ID", "effect": "Decision Impact", "recommendation": "Recommendation"}
            gap_frame = pd.DataFrame(localized["data_gaps"]).rename(columns=columns_map)
            with st.expander(L("전체 Data Gap 표", "Full Data Gap Table"), expanded=len(localized["data_gaps"]) <= 4):
                st.dataframe(gap_frame, hide_index=True, use_container_width=True, height=min(520, 95 + 38 * len(gap_frame)))
        else:
            st.success(T("no_major_gaps"))
    with tabs[2]:
        accepted = [item for item in p.assertions if item.review_status in {"승인", "수정"}]
        if accepted:
            raw_rows = assertion_table_rows(accepted)
            ledger_rows = [localize_assertion_row(row, assertion, lang) for row, assertion in zip(raw_rows, accepted)]
            st.dataframe(pd.DataFrame(ledger_rows), hide_index=True, use_container_width=True, height=min(560, 95 + 38 * len(ledger_rows)))
        else:
            st.info(T("no_accepted_assertions"))
    with tabs[3]:
        audit_rows = [event.to_dict() for event in reversed(p.audit_events)]
        if lang == "en":
            for row in audit_rows:
                row["action"] = audit_action_label(row.get("action", ""), lang)
                row["detail"] = audit_detail_label(row.get("detail", ""), lang)
                row["actor"] = audit_detail_label(row.get("actor", ""), lang)
        audit_frame = pd.DataFrame(audit_rows)
        if lang == "en" and not audit_frame.empty:
            audit_frame = audit_frame.rename(columns={"timestamp_utc": "Timestamp (UTC)", "action": "Action", "detail": "Detail", "actor": "Actor"})
        st.dataframe(audit_frame, hide_index=True, use_container_width=True, height=min(420, 95 + 38 * len(audit_frame)))
        with st.expander(L("기계 판독형 Audit JSON", "Machine-Readable Audit JSON"), expanded=False):
            st.json(localized["audit"])

    accepted = [item for item in p.assertions if item.review_status in {"승인", "수정"}]
    markdown = build_markdown_report(p.assessment_input, assessed, accepted, p.documents, p.project_name, language=lang)
    jsonld = build_jsonld(p.assessment_input, assessed, accepted, p.documents, p.project_id, p.project_name)
    turtle = build_turtle(p.assessment_input, assessed, accepted, p.documents, p.project_id, p.project_name)
    try:
        pdf = build_pdf_report(p.assessment_input, assessed, accepted, p.documents, p.project_name, language=lang)
        pdf_error = None
    except Exception as exc:
        pdf = b""
        pdf_error = str(exc)

    language_suffix = "EN" if lang == "en" else "KO"
    with st.expander(T("downloads"), expanded=False):
        st.caption(L("고객·전문가 공유용 보고서와 온톨로지 교환파일을 내려받습니다.", "Download reviewer-facing reports and ontology exchange files."))
        d1, d2, d3 = st.columns(3)
        d1.download_button(T("advisory_md"), markdown.encode("utf-8"), file_name=f"{p.project_name}_EarlyTox_Report_{language_suffix}.md", mime="text/markdown", use_container_width=True)
        d2.download_button("Ontology JSON-LD", json.dumps(jsonld, ensure_ascii=False, indent=2).encode("utf-8"), file_name=f"{p.project_name}_EarlyTox.jsonld", mime="application/ld+json", use_container_width=True)
        d3.download_button("Ontology Turtle", turtle.encode("utf-8"), file_name=f"{p.project_name}_EarlyTox.ttl", mime="text/turtle", use_container_width=True)
        d4, d5, d6 = st.columns(3)
        d4.download_button(T("gap_csv"), build_gap_csv(assessed, p.assessment_input, language=lang), file_name=f"{p.project_name}_Data_Gaps_{language_suffix}.csv", mime="text/csv", use_container_width=True)
        d5.download_button(T("project_json"), project_json_bytes(p), file_name=f"{p.project_name}.nora.json", mime="application/json", use_container_width=True)
        d6.download_button(T("advisory_pdf"), pdf, file_name=f"{p.project_name}_EarlyTox_Report_{language_suffix}.pdf", mime="application/pdf", use_container_width=True, disabled=not bool(pdf))
        if pdf_error:
            st.warning(T("pdf_disabled", error=pdf_error))

def page_rules() -> None:
    lang = language()
    render_page_header(
        L("06 · 의사결정 논리", "06 · Decision logic"),
        T("rules_title"),
        T("rules_caption"),
    )
    render_section_band(
        L("온톨로지와 규칙의 역할을 분리합니다", "Separate ontology, validation, and decision roles"),
        L(
            "OWL/RDF는 의미관계를 표현하고, SHACL은 필요한 구조와 추적성을 확인하며, Rule Engine은 Data Gap과 Evidence Role을 계산합니다.",
            "OWL/RDF represents semantic relationships, SHACL checks required structure and traceability, and the Rule Engine calculates Data Gaps and Evidence Roles.",
        ),
        "TG-PTO-ET",
    )
    logic_tags = [
        "Product & Exposure", "Toxicity Question", "Context of Use", "Credibility", "Applicability",
        "Human Relevance", "Exposure Translation", "Concordance", "Uncertainty", "Evidence Role", "3Rs Recommendation",
    ]
    tag_html = "".join(f'<span class="nora-tag">{safe_html(item)}</span>' for item in logic_tags)
    st.markdown(f'<div class="nora-tag-row" style="margin:.2rem 0 1rem">{tag_html}</div>', unsafe_allow_html=True)

    with RULE_CATALOG_PATH.open("r", encoding="utf-8") as stream:
        rules = json.load(stream)
    if AI_RULE_CATALOG_PATH.exists():
        with AI_RULE_CATALOG_PATH.open("r", encoding="utf-8") as stream:
            rules.extend(json.load(stream))
    render_section_band(
        T("rule_catalog"),
        L("Rule ID, 발동조건, 결론과 최대 Evidence Role을 검색·필터링할 수 있습니다.", "Search and filter Rule IDs, conditions, conclusions, and maximum Evidence Roles."),
        T("items_count", count=len(rules)),
    )
    f1, f2 = st.columns([2, 1])
    search = f1.text_input(L("규칙 검색", "Search Rules"), placeholder=L("Rule ID, 이름, 조건, 결론", "Rule ID, name, condition, or conclusion"), key=f"rule_search_{lang}")
    role_options = ["__all__"] + sorted({item.get("maximum_role", "") for item in rules if item.get("maximum_role")})
    selected_role = f2.selectbox(
        L("최대 Evidence Role", "Maximum Evidence Role"),
        role_options,
        format_func=lambda value: L("전체", "All") if value == "__all__" else value,
        key=f"rule_role_{lang}",
    )
    filtered_rules = []
    for item in rules:
        if selected_role != "__all__" and item.get("maximum_role") != selected_role:
            continue
        if search:
            haystack = " ".join(str(item.get(key, "")) for key in ["rule_id", "name_ko", "name_en", "condition", "condition_en", "conclusion", "conclusion_en"]).lower()
            if search.lower() not in haystack:
                continue
        filtered_rules.append(item)

    if lang == "en":
        display_rules = [
            {
                "Rule ID": item.get("rule_id"),
                "Name": item.get("name_en", item.get("name_ko")),
                "Condition": item.get("condition_en", item.get("condition")),
                "Conclusion": item.get("conclusion_en", item.get("conclusion")),
                "Maximum Role": item.get("maximum_role"),
            }
            for item in filtered_rules
        ]
    else:
        display_rules = [
            {
                "Rule ID": item.get("rule_id"),
                "이름": item.get("name_ko"),
                "조건": item.get("condition"),
                "결론": item.get("conclusion"),
                "최대 Role": item.get("maximum_role"),
            }
            for item in filtered_rules
        ]
    st.dataframe(pd.DataFrame(display_rules), hide_index=True, use_container_width=True, height=min(560, 95 + 42 * len(display_rules)))

    core_text = ONTOLOGY_CORE_PATH.read_text(encoding="utf-8")
    shape_text = ONTOLOGY_SHAPES_PATH.read_text(encoding="utf-8")
    with st.expander(L("OWL/RDF Core 보기", "View OWL/RDF Core"), expanded=False):
        st.code(core_text, language="turtle", line_numbers=True)
        st.download_button("TG-PTO-ET Core TTL", core_text.encode("utf-8"), file_name="tg_pto_et_core.ttl", mime="text/turtle")
    with st.expander(L("SHACL Shapes 보기", "View SHACL Shapes"), expanded=False):
        st.code(shape_text, language="turtle", line_numbers=True)
        st.download_button("TG-PTO-ET SHACL TTL", shape_text.encode("utf-8"), file_name="tg_pto_et_shapes.ttl", mime="text/turtle")

    constraints = (
        [
            ("Model Accuracy", "높은 모델 정확도 ≠ 현재 후보에 대한 높은 적용성"),
            ("Negative AI", "음성 AI 예측 ≠ 독성 부재"),
            ("Negative NAM", "음성 NAM 결과 ≠ Reliable Negative"),
            ("Applicability", "Out-of-domain 예측 ≠ 신뢰 가능한 근거"),
            ("Exposure", "명목농도 ≠ 표적부위 노출"),
            ("Weight of Evidence", "하나의 근거 흐름 ≠ Weight of Evidence"),
            ("Replacement", "특정 endpoint 대체 ≠ 전체 독성패키지 대체"),
            ("Missing Evidence", "자료 없음 ≠ 음성 근거"),
        ]
        if lang == "ko"
        else [
            ("Model Accuracy", "High model accuracy ≠ high applicability to the current candidate"),
            ("Negative AI", "Negative AI prediction ≠ absence of toxicity"),
            ("Negative NAM", "Negative NAM result ≠ Reliable Negative"),
            ("Applicability", "Out-of-domain prediction ≠ reliable evidence"),
            ("Exposure", "Nominal concentration ≠ target-site exposure"),
            ("Weight of Evidence", "One evidence stream ≠ weight of evidence"),
            ("Replacement", "Replacement of one endpoint ≠ replacement of the entire toxicology package"),
            ("Missing Evidence", "Missing evidence ≠ negative evidence"),
        ]
    )
    render_section_band(T("top_constraints"), L("모든 평가와 자문에 우선 적용되는 논리제약입니다.", "These constraints take priority across all assessments and advisory outputs."), "8")
    cards = [render_advisory_card(code, title, "") for code, title in constraints]
    st.markdown(f'<div class="nora-advisory-grid">{"".join(cards)}</div>', unsafe_allow_html=True)



_apply_pending_widget_state()
header()
page = sidebar()
status_strip()
pipeline(page)

if page == "overview":
    page_project_overview()
elif page == "consulting":
    page_consulting_studio()
elif page == "documents":
    page_documents()
elif page == "assertions":
    page_assertion_review()
elif page == "assessment":
    page_assessment_input()
elif page == "results":
    page_results()
elif page == "rules":
    page_rules()


# --- Regulatory-status notice ---
try:
    _nora_lang = language()
    if _nora_lang == "en":
        _notice = (
            "Regulatory-status notice: R0–R5 Evidence Roles and ET-R001–ET-R015 role caps "
            "are NORA's conservative internal decision-support policies. They are not regulatory "
            "classifications, agency approvals, animal-test waivers, or guarantees of regulatory acceptance. "
            "FDA AI/NAM documents cited by NORA are draft and nonbinding unless explicitly identified otherwise "
            "in the verified reference registry."
        )
    else:
        _notice = (
            "규제 상태 고지: R0–R5 Evidence Role과 ET-R001–ET-R015 역할 상한은 NORA의 보수적 내부 "
            "의사결정 지원 정책입니다. 규제기관이 정한 법적 분류, 승인, 동물시험 면제 또는 규제 수용 "
            "보장이 아닙니다. NORA가 인용하는 FDA AI/NAM 문서는 검증된 레퍼런스 레지스트리에 달리 "
            "표시되지 않는 한 초안이며 비구속적입니다."
        )
    render_footer_notice(_notice)
except Exception:
    pass
