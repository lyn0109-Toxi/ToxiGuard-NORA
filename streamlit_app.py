from __future__ import annotations

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
)
from nora.cases import CASE_BUILDERS, load_case
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


APP_ROOT = Path(__file__).resolve().parent
RULE_CATALOG_PATH = APP_ROOT / "data" / "rule_catalog.json"
ONTOLOGY_CORE_PATH = APP_ROOT / "ontology" / "tg_pto_et_core.ttl"
ONTOLOGY_SHAPES_PATH = APP_ROOT / "ontology" / "tg_pto_et_shapes.ttl"

st.set_page_config(
    page_title="ToxiGuard NORA EarlyTox",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
:root {
  --nora-navy:#10243f;
  --nora-blue:#176b87;
  --nora-teal:#138a82;
  --nora-mint:#eaf7f4;
  --nora-ice:#eff7fb;
  --nora-line:#d9e2ea;
  --nora-muted:#5d6978;
  --nora-red:#b23a48;
  --nora-amber:#b56f00;
  --nora-green:#17754d;
}
.stApp { background:#f4f7fa; }
.block-container { max-width:1420px; padding-top:1.2rem; padding-bottom:5rem; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#10243f,#0e3951); }
[data-testid="stSidebar"] * { color:#f4fbff; }
[data-testid="stSidebar"] input, [data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] [data-baseweb="select"] > div { color:#10243f; background:#fff; }
[data-testid="stSidebar"] .stButton > button { color:#10243f; background:#fff; border:0; font-weight:800; }
.nora-header { padding:1.45rem 1.55rem; border-radius:18px; background:linear-gradient(135deg,#10243f,#105b71); color:white; box-shadow:0 16px 38px rgba(16,36,63,.16); margin-bottom:1rem; }
.nora-header h1 { margin:0; font-size:2.05rem; line-height:1.15; }
.nora-header p { margin:.45rem 0 0; color:#d6edf0; }
.nora-banner { padding:.9rem 1rem; border:1px solid #cddbe4; border-left:5px solid #138a82; border-radius:12px; background:white; margin-bottom:1rem; color:#394657; }
.nora-card { padding:1rem 1.05rem; border:1px solid #d9e2ea; border-radius:15px; background:white; box-shadow:0 10px 24px rgba(16,36,63,.055); }
.role-card { min-height:230px; padding:1.4rem; border-radius:17px; color:white; background:linear-gradient(135deg,#10243f,#105b71); }
.role-code { font-size:3.1rem; font-weight:900; line-height:1; margin-top:.7rem; }
.role-name { font-size:1.45rem; font-weight:850; margin:.25rem 0 .55rem; }
.role-desc { color:#d6edf0; }
.gate-pass { border-left:5px solid #17754d !important; }
.gate-cond { border-left:5px solid #b56f00 !important; }
.gate-fail { border-left:5px solid #b23a48 !important; }
.small-muted { color:#5d6978; font-size:.82rem; }
.pipeline { display:grid; grid-template-columns:repeat(6,1fr); gap:.55rem; margin:1rem 0; }
.pipe-step { padding:.8rem .6rem; border:1px solid #d9e2ea; border-radius:12px; background:#fff; text-align:center; font-size:.78rem; color:#394657; }
.pipe-step strong { display:block; color:#173b63; margin-bottom:.25rem; }
.status-strip { display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:.8rem; margin:.85rem 0 1rem; }
.status-box { padding:.85rem 1rem; border:1px solid #d9e2ea; border-radius:13px; background:#fff; }
.status-box span { display:block; color:#5d6978; font-size:.75rem; font-weight:750; }
.status-box strong { display:block; color:#10243f; font-size:1.05rem; margin-top:.25rem; }
.language-box { display:flex; justify-content:flex-end; align-items:center; min-height:100%; padding-top:.2rem; }
.language-box [data-testid="stRadio"] > label { display:none; }
.language-box [role="radiogroup"] { justify-content:flex-end; gap:.25rem; background:#fff; padding:.28rem; border:1px solid #d9e2ea; border-radius:999px; box-shadow:0 8px 22px rgba(16,36,63,.08); }
.language-box [role="radiogroup"] label { padding:.15rem .35rem; }
@media(max-width:1000px){.pipeline{grid-template-columns:repeat(3,1fr)}.status-strip{grid-template-columns:repeat(2,1fr)}}
@media(max-width:650px){.pipeline{grid-template-columns:1fr}.status-strip{grid-template-columns:1fr}}
</style>
""",
    unsafe_allow_html=True,
)


NAV_PAGES = PAGE_IDS



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


@st.cache_resource
def get_store() -> ProjectStore:
    data_dir = Path(os.environ.get("NORA_DATA_DIR", APP_ROOT / ".nora_data"))
    return ProjectStore(data_dir / "projects.db")


def project() -> ProjectBundle:
    if "nora_project" not in st.session_state:
        st.session_state.nora_project = ProjectBundle.new(name=L("새 EarlyTox 프로젝트", "New EarlyTox Project"))
    return st.session_state.nora_project


def set_project(value: ProjectBundle, page: str = "overview") -> None:
    st.session_state.nora_project = value
    st.session_state.assessment_result = None
    st.session_state.nav_page = page


def result():
    return st.session_state.get("assessment_result")


def invalidate_result() -> None:
    st.session_state.assessment_result = None
    project().last_result = None


def add_event(action: str, detail: str) -> None:
    project().add_event(action, detail, project().owner or "현재 사용자")


def _optional_float(value: object) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    return max(0.0, min(100.0, number))


def _status_counts() -> dict[str, int]:
    counts = {status: 0 for status in REVIEW_STATUS_OPTIONS}
    for assertion in project().assertions:
        counts[assertion.review_status] = counts.get(assertion.review_status, 0) + 1
    return counts


def header() -> None:
    left, right = st.columns([8.6, 1.4], gap="medium")
    with right:
        st.markdown('<div class="language-box">', unsafe_allow_html=True)
        st.radio(
            T("language"),
            ["한국어", "English"],
            index=0 if language() == "ko" else 1,
            horizontal=True,
            key="nora_language",
            label_visibility="collapsed",
        )
        st.markdown('</div>', unsafe_allow_html=True)
    with left:
        st.markdown(
            f"""
<div class="nora-header">
  <h1>ToxiGuard NORA EarlyTox</h1>
  <p>{T('header_description')}</p>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown(
        f"""
<div class="nora-banner">
  <strong>{T('tagline')}</strong><br>
  {T('header_principle')}
</div>
""",
        unsafe_allow_html=True,
    )


def status_strip() -> None:
    p = project()
    counts = _status_counts()
    current = result()
    role = current.evidence_role_code if current else T("not_assessed")
    approved_count = counts.get("승인", 0) + counts.get("수정", 0)
    st.markdown(
        f"""
<div class="status-strip">
  <div class="status-box"><span>{T('project')}</span><strong>{p.project_name}</strong></div>
  <div class="status-box"><span>{T('documents')}</span><strong>{T('items_count', count=len(p.documents))}</strong></div>
  <div class="status-box"><span>{T('assertions')}</span><strong>{T('items_count', count=len(p.assertions))}</strong></div>
  <div class="status-box"><span>{T('approved_corrected')}</span><strong>{T('items_count', count=approved_count)}</strong></div>
  <div class="status-box"><span>{T('current_role')}</span><strong>{role}</strong></div>
</div>
""",
        unsafe_allow_html=True,
    )


def pipeline() -> None:
    steps = [
        (L("1. 문서", "1. Documents"), L("AI/NAM/PK 보고서", "AI/NAM/PK reports")),
        (L("2. 추출", "2. Extraction"), L("출처연결 Assertion", "Source-linked Assertions")),
        (L("3. 검토", "3. Review"), L("승인·수정·거절", "Approve · correct · reject")),
        (L("4. 검증", "4. Validation"), L("Gate·Data Gap", "Gates · Data Gaps")),
        (L("5. 판단", "5. Classification"), "Evidence Role R0–R5"),
        (L("6. 자문", "6. Advisory"), L("다음 근거·3Rs 권고", "Next evidence · 3Rs recommendation")),
    ]
    html = ''.join(f'<div class="pipe-step"><strong>{title}</strong>{body}</div>' for title, body in steps)
    st.markdown(f'<div class="pipeline">{html}</div>', unsafe_allow_html=True)


def sidebar() -> str:
    p = project()
    with st.sidebar:
        st.markdown("## NORA EarlyTox")
        st.caption(
            L(
                f"NORA v{__version__} · {__ontology_version__} · 초기 간독성 vertical slice",
                f"NORA v{__version__} · {__ontology_version__} · early-hepatotoxicity vertical slice",
            )
        )

        with st.expander(T("project_management"), expanded=True):
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
                key="saved_project_selector",
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

        legacy_pages = {
            "프로젝트 개요": "overview", "문서 근거": "documents", "근거 검토": "assertions",
            "평가 입력": "assessment", "결과·보고서": "results", "규칙·온톨로지": "rules",
        }
        if st.session_state.get("nav_page") in legacy_pages:
            st.session_state.nav_page = legacy_pages[st.session_state.nav_page]
        if st.session_state.get("nav_page") not in NAV_PAGES:
            st.session_state.nav_page = "overview"
        page = st.radio(
            T("workspace"),
            NAV_PAGES,
            format_func=lambda page_id: _page(page_id),
            key="nav_page",
        )
        st.divider()
        st.caption(T("prototype_note"))
    return page


def page_project_overview() -> None:
    p = project()
    st.subheader(T("project_overview"))
    st.write(T("overview_text"))
    pipeline()

    left, right = st.columns([1.12, 0.88], gap="large")
    with left:
        st.markdown(f"### {T('current_question')}")
        cou = p.assessment_input.context_of_use
        if cou.question_of_interest:
            st.info(cou.question_of_interest)
        else:
            st.warning(T("qoi_missing"))
        table = [
            {T("item"): T("assessment_objective"), T("current_value"): fmt(cou.objective)},
            {T("item"): T("development_stage"), T("current_value"): fmt(cou.development_stage)},
            {T("item"): "Endpoint", T("current_value"): fmt(cou.target_endpoint)},
            {T("item"): T("intended_role"), T("current_value"): fmt(cou.intended_evidence_role)},
            {T("item"): T("jurisdiction_context"), T("current_value"): fmt(cou.jurisdiction)},
        ]
        st.dataframe(pd.DataFrame(table), hide_index=True, use_container_width=True)

        st.markdown(f"### {T('product_context')}")
        product = p.assessment_input.product
        product_rows = [
            {T("item"): T("candidate"), T("current_value"): product.product_name or T("not_entered")},
            {T("item"): "Modality", T("current_value"): fmt(product.modality)},
            {T("item"): T("target_mechanism"), T("current_value"): product.target_mechanism or T("not_entered")},
            {T("item"): T("carrier_formulation"), T("current_value"): product.carrier_formulation or T("not_entered")},
            {T("item"): T("route_exposure"), T("current_value"): f"{fmt(product.route)} / {fmt(product.exposure_pattern)}"},
        ]
        st.dataframe(pd.DataFrame(product_rows), hide_index=True, use_container_width=True)

    with right:
        st.markdown(f"### {T('judgments_made')}")
        for role in range(6):
            code, title, description = role_definition(role, language())
            st.markdown(f"**{code} · {title}**  \n{description}")
        st.markdown(f"### {T('judgments_not_made')}")
        st.error(T("not_decide_text"))

    st.markdown(f"### {T('quick_start')}")
    q1, q2, q3 = st.columns(3)
    if q1.button(T("start_upload"), use_container_width=True, key=f"quick_upload_{p.project_id}"):
        st.session_state.nav_page = "documents"
        st.rerun()
    if q2.button(T("start_manual"), use_container_width=True, key=f"quick_manual_{p.project_id}"):
        st.session_state.nav_page = "assessment"
        st.rerun()
    if q3.button(T("gplct_case"), use_container_width=True, key=f"quick_gplct_{p.project_id}"):
        demo_project = ProjectBundle.new(name="GP-L-CT EarlyTox")
        demo_project.assessment_input = load_case("GP-L-CT — 적용범위 밖 음성예측", language())
        set_project(demo_project, "assessment")
        st.rerun()


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
    st.subheader(T("document_workspace"))
    st.caption(T("document_workspace_caption"))

    upload = st.file_uploader(
        T("document_uploader"),
        type=["pdf", "docx", "txt", "md", "csv", "xlsx", "xlsm", "json"],
        accept_multiple_files=True,
        key=f"doc_upload_{p.project_id}",
    )
    manual = st.text_area(
        T("manual_evidence"),
        height=125,
        key=f"manual_evidence_{p.project_id}",
        placeholder=T("manual_evidence_placeholder"),
    )
    c1, c2 = st.columns([1, 1])
    if c1.button(T("process_documents"), type="primary", use_container_width=True, disabled=not bool(upload), key=f"process_docs_{p.project_id}"):
        with st.spinner(T("processing_documents")):
            added, skipped = _process_files(upload or [])
        st.success(T("documents_added", added=added, skipped=skipped))
        st.rerun()
    if c2.button(T("add_pasted_text"), use_container_width=True, disabled=not manual.strip(), key=f"add_manual_{p.project_id}"):
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

    st.markdown(f"### {T('document_inventory')}")
    inventory_rows = [localize_document_row(document_inventory_row(item), language()) for item in p.documents]
    st.dataframe(pd.DataFrame(inventory_rows), hide_index=True, use_container_width=True)

    selected_name = st.selectbox(T("review_document"), [item.name for item in p.documents], key=f"selected_doc_{p.project_id}")
    selected = next(item for item in p.documents if item.name == selected_name)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(T("evidence_segments"), len(selected.segments))
    m2.metric(T("characters_extracted"), len(selected.extracted_text))
    m3.metric(T("auto_assertions"), sum(1 for item in p.assertions if item.source_document_id == selected.document_id))
    m4.metric(T("warnings"), len(selected.warnings))

    if selected.warnings:
        with st.expander(T("document_warnings"), expanded=True):
            for warning in selected.warnings:
                st.warning(warning)

    if selected.segments:
        location = st.selectbox(T("source_location"), [segment.location for segment in selected.segments], key=f"segment_{selected.document_id}")
        segment = next(item for item in selected.segments if item.location == location)
        st.text_area(T("extracted_text"), segment.text, height=330, disabled=True, key=f"segment_text_{selected.document_id}_{location}")

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
    st.subheader(T("assertion_review"))
    st.caption(T("assertion_review_caption"))

    if not p.assertions:
        st.info(T("no_assertions"))
        return

    counts = _status_counts()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(T("total"), len(p.assertions))
    c2.metric(T("proposed"), counts.get("제안됨", 0))
    c3.metric(T("approved_corrected"), counts.get("승인", 0) + counts.get("수정", 0))
    c4.metric(T("rejected"), counts.get("거절", 0))

    all_value = "__all__"
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
        num_rows="fixed",
        key=f"assertion_editor_{p.project_id}_{selected_category}_{selected_status}_{selected_document}_{lang}",
        disabled=disabled,
        column_config={
            status_column: st.column_config.SelectboxColumn(status_column, options=review_options, required=True),
            confidence_column: st.column_config.NumberColumn(confidence_column, min_value=0.0, max_value=1.0, format="%.2f"),
            excerpt_column: st.column_config.TextColumn(excerpt_column, width="large"),
            value_column: st.column_config.TextColumn(value_column, width="medium"),
            note_column: st.column_config.TextColumn(note_column, width="medium"),
        },
    )

    b1, b2, b3 = st.columns(3)
    if b1.button(T("save_edits"), type="primary", use_container_width=True, key=f"save_assert_{p.project_id}_{lang}"):
        internal_rows = [internalize_assertion_row(row, lang) for row in edited.to_dict("records")]
        updated_subset = assertions_from_table_rows(internal_rows, p.assertions)
        updated_by_id = {item.assertion_id: item for item in updated_subset}
        p.assertions = [updated_by_id.get(item.assertion_id, item) for item in p.assertions]
        add_event("Assertion 검토 저장", f"필터 결과 {len(updated_subset)}개")
        invalidate_result()
        st.success(T("review_saved"))
        st.rerun()
    if b2.button(T("approve_filtered"), use_container_width=True, key=f"approve_filter_{p.project_id}_{lang}"):
        ids = {item.assertion_id for item in filtered}
        for item in p.assertions:
            if item.assertion_id in ids:
                item.review_status = "승인"
        add_event("Assertion 일괄 승인", f"{len(ids)}개")
        invalidate_result()
        st.rerun()
    if b3.button(T("apply_approved"), use_container_width=True, key=f"apply_assert_{p.project_id}_{lang}"):
        p.assessment_input = apply_reviewed_assertions(p.assessment_input, p.assertions)
        add_event("승인 Assertion 적용", f"승인·수정 {sum(1 for item in p.assertions if item.review_status in {'승인','수정'})}개")
        invalidate_result()
        st.success(T("approved_applied"))
        st.session_state.nav_page = "assessment"
        st.rerun()

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
            p13, p14, p15, p16 = st.columns(4)
            human_cmax = p13.text_input(L("예상 Cmax", "Expected Cmax"), value=current.product.human_cmax, key=f"{prefix}_product_cmax")
            human_auc = p14.text_input(L("예상 AUC", "Expected AUC"), value=current.product.human_auc, key=f"{prefix}_product_auc")
            distribution_options = ["없음", "정성적 자료", "정량적 자료"]
            distribution_status = sb(p15, "Biodistribution", "Biodistribution", distribution_options, current.product.distribution_status, "product_distribution")
            rep_options = ["불명확", "부분적으로 확인", "임상제품 대표성 확인"]
            representativeness = sb(p16, "시험물질 대표성", "Test-Article Representativeness", rep_options, current.product.test_article_representativeness, "product_representative")

        with tabs[2]:
            use_ai = st.checkbox(L("AI/in silico 근거 사용", "Use AI / In Silico Evidence"), value=current.ai_model.use_ai, key=f"{prefix}_ai_use")
            a1, a2, a3 = st.columns(3)
            model_name = a1.text_input(L("모델명", "Model Name"), value=current.ai_model.model_name, key=f"{prefix}_ai_name")
            model_version = a2.text_input(L("모델 버전", "Model Version"), value=current.ai_model.model_version, key=f"{prefix}_ai_version")
            model_type_options = ["Rule-based QSAR", "Statistical QSAR", "Machine learning classifier", "Deep learning / GNN", "Transcriptomic signature model"]
            model_type = sb(a3, "모델 유형", "Model Type", model_type_options, current.ai_model.model_type, "ai_type")
            a4, a5, a6 = st.columns(3)
            ai_endpoint = sb(a4, "예측 Endpoint", "Predicted Endpoint", endpoint_options, current.ai_model.endpoint, "ai_endpoint")
            result_options = ["음성 / 낮은 위험 예측", "양성 / 위험 신호", "경계 / 불확실"]
            ai_result = sb(a5, "AI 예측 결과", "AI Prediction Result", result_options, current.ai_model.result, "ai_result")
            ai_probability = a6.text_input(L("예측 확률(%)", "Predicted Probability (%)"), value="" if current.ai_model.probability_percent is None else str(current.ai_model.probability_percent), key=f"{prefix}_ai_probability")
            domain_values = ["저분자", "올리고뉴클레오타이드", "나노의약품", "바이오의약품"]
            domain_modalities = st.multiselect(
                L("학습·검증자료 Modality", "Modalities in Training / Validation Data"),
                domain_values,
                default=current.ai_model.domain_modalities,
                format_func=fmt,
                key=f"{prefix}_ai_domain_modalities",
            )
            a7, a8, a9, a10 = st.columns(4)
            ext_options = ["확인됨", "부분적으로 확인", "없음", "불명확"]
            external_validation = sb(a7, "외부 독립검증", "Independent External Validation", ext_options, current.ai_model.external_validation, "ai_external")
            sensitivity = a8.text_input("Sensitivity (%)", value="" if current.ai_model.sensitivity_percent is None else str(current.ai_model.sensitivity_percent), key=f"{prefix}_ai_sensitivity")
            specificity = a9.text_input("Specificity (%)", value="" if current.ai_model.specificity_percent is None else str(current.ai_model.specificity_percent), key=f"{prefix}_ai_specificity")
            fnr = a10.text_input("False-negative rate (%)", value="" if current.ai_model.false_negative_rate_percent is None else str(current.ai_model.false_negative_rate_percent), key=f"{prefix}_ai_fnr")
            a11, a12 = st.columns(2)
            cal_options = ["검증됨", "부분 검증", "미검증", "불명확"]
            calibration = sb(a11, "확률 Calibration", "Probability Calibration", cal_options, current.ai_model.calibration_status, "ai_calibration")
            domain_options = ["자동 평가", "In-domain", "Borderline", "Out-of-domain", "Unknown"]
            domain_status = sb(a12, "후보 Applicability Domain", "Candidate Applicability Domain", domain_options, current.ai_model.domain_status, "ai_domain_status")
            ai_source = st.text_input(L("모델 출처", "Model Source"), value=current.ai_model.source, key=f"{prefix}_ai_source")
            known_limitations = st.text_area(L("알려진 한계", "Known Limitations"), value=current.ai_model.known_limitations, height=85, key=f"{prefix}_ai_limitations")

        with tabs[3]:
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
            n7, n8, n9, n10 = st.columns(4)
            control_options = ["유효", "실패", "없음 / 불명확"]
            positive_control = sb(n7, "양성대조군", "Positive Control", control_options, current.nam_assay.positive_control, "nam_positive")
            negative_control = sb(n8, "음성대조군", "Negative Control", control_options, current.nam_assay.negative_control, "nam_negative")
            carrier_options = ["포함", "미포함", "해당 없음"]
            carrier_control = sb(n9, "Carrier-only", "Carrier-Only Control", carrier_options, current.nam_assay.carrier_only_control, "nam_carrier_control")
            active_control = sb(n10, "Active-only", "Active-Only Control", carrier_options, current.nam_assay.active_only_control, "nam_active_control")
            n11, n12, n13, n14 = st.columns(4)
            protocol_options = ["완결", "부분적", "불충분"]
            protocol = sb(n11, "프로토콜 완결성", "Protocol Completeness", protocol_options, current.nam_assay.protocol_completeness, "nam_protocol")
            measured_options = ["측정됨", "부분 측정", "측정 안 됨"]
            measured = sb(n12, "Free/세포내 노출", "Free / Intracellular Exposure", measured_options, current.nam_assay.measured_exposure, "nam_measured")
            qivive_options = ["수행됨", "초기 연결", "없음"]
            qivive = sb(n13, "QIVIVE/PBPK", "QIVIVE / PBPK", qivive_options, current.nam_assay.qivive_pbpk, "nam_qivive")
            repro_options = ["Donor/lot/반복 재현성 확인", "일부 확인", "확인되지 않음"]
            reproducibility = sb(n14, "재현성", "Reproducibility", repro_options, current.nam_assay.reproducibility, "nam_repro")
            nominal_exposure = st.text_input(L("명목 농도", "Nominal Concentration"), value=current.nam_assay.nominal_exposure, key=f"{prefix}_nam_nominal")
            endpoint_values = ["Cell viability / ATP", "미토콘드리아 기능", "산화스트레스", "ALT / AST / GLDH", "Cytokine", "담즙산 수송", "CYP 대사기능", "Omics signature"]
            nam_endpoints = st.multiselect("NAM Endpoint", endpoint_values, default=current.nam_assay.endpoints, format_func=fmt, key=f"{prefix}_nam_endpoints")

        with tabs[4]:
            e1, e2, e3 = st.columns(3)
            mechanistic = e1.checkbox(L("기전 기반 근거", "Mechanistic Evidence"), value=current.supporting_evidence.mechanistic_evidence, key=f"{prefix}_ev_mechanistic")
            class_evidence = e2.checkbox(L("동일계열·임상 Class 근거", "Class / Clinical Evidence"), value=current.supporting_evidence.class_or_clinical_evidence, key=f"{prefix}_ev_class")
            quantitative_bio = e3.checkbox(L("정량적 Biodistribution", "Quantitative Biodistribution"), value=current.supporting_evidence.quantitative_biodistribution, key=f"{prefix}_ev_bio")
            e4, e5, e6 = st.columns(3)
            pk_tk = e4.checkbox(L("PK/TK 및 노출-반응", "PK/TK and Exposure-Response"), value=current.supporting_evidence.pk_tk_evidence, key=f"{prefix}_ev_pktk")
            invivo = e5.checkbox(L("기존 in vivo 독성자료", "Existing In Vivo Toxicity Evidence"), value=current.supporting_evidence.existing_in_vivo_evidence, key=f"{prefix}_ev_invivo")
            human_evidence = e6.checkbox(L("사람·임상·사람 조직 근거", "Human / Clinical / Human-Tissue Evidence"), value=current.supporting_evidence.human_evidence, key=f"{prefix}_ev_human")
            g1, g2, g3, g4 = st.columns(4)
            traceable = g1.checkbox(L("근거 추적 가능", "Evidence Traceable"), value=current.supporting_evidence.evidence_traceable, key=f"{prefix}_gov_trace")
            assertions_reviewed = g2.checkbox(L("Assertion 검토 완료", "Assertions Reviewed"), value=current.supporting_evidence.assertions_reviewed, key=f"{prefix}_gov_assert")
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
            domain_modalities=domain_modalities,
            external_validation=external_validation,
            sensitivity_percent=_optional_float(sensitivity),
            specificity_percent=_optional_float(specificity),
            false_negative_rate_percent=_optional_float(fnr),
            calibration_status=calibration,
            domain_status=domain_status,
            source=ai_source,
            known_limitations=known_limitations,
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
    st.subheader(T("structured_input"))
    st.caption(T("structured_input_caption"))
    updated = _assessment_form()
    if updated:
        project().assessment_input = updated
        project().touch()
        add_event("구조화 평가 입력 저장", updated.product.product_name or "후보 미입력")
        invalidate_result()
        st.success(T("assessment_saved"))
        st.rerun()


def _score_card(label: str, value: Any) -> None:
    with st.container(border=True):
        st.caption(label)
        if isinstance(value, (float, int)):
            st.markdown(f"### {float(value):.1f} / 4")
            st.progress(max(0.0, min(1.0, float(value) / 4.0)))
        else:
            st.markdown(f"### {value}")


def _run_assessment() -> None:
    p = project()
    assessed = evaluate(p.assessment_input)
    st.session_state.assessment_result = assessed
    p.last_result = assessed.to_dict()
    add_event("EarlyTox 평가 실행", f"{assessed.evidence_role_code} - {assessed.evidence_role_name}")


def page_results() -> None:
    p = project()
    lang = language()
    st.subheader(T("results_title"))
    st.caption(T("results_caption"))

    if st.button(T("run_assessment"), type="primary", use_container_width=True, key=f"run_assessment_{p.project_id}"):
        _run_assessment()
        st.rerun()

    assessed = result()
    if not assessed:
        st.info(T("assessment_placeholder"))
        return

    localized = localize_result(assessed, p.assessment_input, lang)
    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        st.markdown(
            f"""
<div class="role-card">
  <div class="small-muted" style="color:#cfe7ec">{T('current_role')}</div>
  <div class="role-code">{localized['evidence_role_code']}</div>
  <div class="role-name">{localized['evidence_role_name']}</div>
  <div class="role-desc">{localized['evidence_role_description']}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(f"### {T('animal_recommendation')}")
        if assessed.evidence_role <= 2:
            st.error(localized["animal_use_status"])
        elif assessed.evidence_role == 3:
            st.warning(localized["animal_use_status"])
        else:
            st.success(localized["animal_use_status"])
        st.write(localized["animal_use_description"])
        st.metric(T("model_risk"), localized["model_risk"])
        st.metric(T("residual_uncertainty"), localized["residual_uncertainty"])
        st.metric(T("independent_streams"), localized["evidence_stream_count"])

    st.markdown(f"### {T('assessment_dimensions')}")
    score_items = list(localized["scores"].items())
    columns = st.columns(3)
    for index, (label, value) in enumerate(score_items):
        with columns[index % 3]:
            _score_card(label, value)

    tabs = st.tabs(["Hard Gate", T("data_gap"), T("explainable_advisory"), T("evidence_ledger"), T("audit_trail")])
    with tabs[0]:
        for gate in localized["gates"]:
            status_internal = next((item.status for item in assessed.gates if value_label(item.status, lang) == gate["status"] and value_label(item.gate, lang) == gate["gate"]), None)
            # status_internal fallback is based on the localized label
            css = "gate-pass" if gate["status"] in {"통과", "Pass"} else "gate-cond" if gate["status"] in {"조건부", "Conditional"} else "gate-fail"
            with st.container(border=True):
                st.markdown(
                    f"<div class='{css}' style='padding-left:.75rem'><strong>{gate['gate']} · {gate['status']}</strong><br>{gate['rationale']}<br><span class='small-muted'>{T('impact')}: {gate['effect']}</span></div>",
                    unsafe_allow_html=True,
                )
    with tabs[1]:
        if localized["data_gaps"]:
            if lang == "ko":
                columns_map = {"code": "Gap Code", "title": "제목", "description": "설명", "criticality": "중요도", "rule_id": "Rule ID", "effect": "판정 영향", "recommendation": "권고"}
            else:
                columns_map = {"code": "Gap Code", "title": "Title", "description": "Description", "criticality": "Criticality", "rule_id": "Rule ID", "effect": "Decision Impact", "recommendation": "Recommendation"}
            gap_frame = pd.DataFrame(localized["data_gaps"]).rename(columns=columns_map)
            st.dataframe(gap_frame, hide_index=True, use_container_width=True)
        else:
            st.success(T("no_major_gaps"))
    with tabs[2]:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"#### {T('observation')}")
            for item in localized["observations"]:
                st.write(f"- {item}")
            st.markdown(f"#### {T('interpretation')}")
            for item in localized["interpretations"]:
                st.write(f"- {item}")
        with c2:
            st.markdown(f"#### {T('development_relevance')}")
            for item in localized["development_relevance"]:
                st.write(f"- {item}")
            st.markdown(f"#### {T('recommendations')}")
            for item in localized["recommendations"]:
                st.write(f"- {item}")
    with tabs[3]:
        accepted = [item for item in p.assertions if item.review_status in {"승인", "수정"}]
        if accepted:
            raw_rows = assertion_table_rows(accepted)
            ledger_rows = [localize_assertion_row(row, assertion, lang) for row, assertion in zip(raw_rows, accepted)]
            st.dataframe(pd.DataFrame(ledger_rows), hide_index=True, use_container_width=True)
        else:
            st.info(T("no_accepted_assertions"))
    with tabs[4]:
        audit_rows = [event.to_dict() for event in reversed(p.audit_events)]
        if lang == "en":
            for row in audit_rows:
                row["action"] = audit_action_label(row.get("action", ""), lang)
                row["detail"] = audit_detail_label(row.get("detail", ""), lang)
                row["actor"] = audit_detail_label(row.get("actor", ""), lang)
        audit_frame = pd.DataFrame(audit_rows)
        if lang == "en" and not audit_frame.empty:
            audit_frame = audit_frame.rename(columns={"timestamp_utc": "Timestamp (UTC)", "action": "Action", "detail": "Detail", "actor": "Actor"})
        st.dataframe(audit_frame, hide_index=True, use_container_width=True)
        st.json(localized["audit"])

    st.markdown(f"### {T('downloads')}")
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
    st.subheader(T("rules_title"))
    st.caption(T("rules_caption"))
    st.code(
        "Product & Exposure → Toxicity Question → AI/NAM Context of Use → Credibility → Applicability → Human/Exposure Relevance → Concordance → Uncertainty → Evidence Role → 3Rs Recommendation",
        language="text",
    )
    with RULE_CATALOG_PATH.open("r", encoding="utf-8") as stream:
        rules = json.load(stream)
    st.markdown(f"### {T('rule_catalog')}")
    if lang == "en":
        display_rules = [
            {
                "Rule ID": item.get("rule_id"),
                "Name": item.get("name_en", item.get("name_ko")),
                "Condition": item.get("condition_en", item.get("condition")),
                "Conclusion": item.get("conclusion_en", item.get("conclusion")),
                "Maximum Role": item.get("maximum_role"),
            }
            for item in rules
        ]
    else:
        display_rules = rules
    st.dataframe(pd.DataFrame(display_rules), hide_index=True, use_container_width=True)

    t1, t2 = st.tabs(["OWL/RDF Core", "SHACL Shapes"])
    core_text = ONTOLOGY_CORE_PATH.read_text(encoding="utf-8")
    shape_text = ONTOLOGY_SHAPES_PATH.read_text(encoding="utf-8")
    with t1:
        st.code(core_text, language="turtle")
        st.download_button("TG-PTO-ET Core TTL", core_text.encode("utf-8"), file_name="tg_pto_et_core.ttl", mime="text/turtle")
    with t2:
        st.code(shape_text, language="turtle")
        st.download_button("TG-PTO-ET SHACL TTL", shape_text.encode("utf-8"), file_name="tg_pto_et_shapes.ttl", mime="text/turtle")

    st.markdown(f"### {T('top_constraints')}")
    if lang == "ko":
        st.markdown(
            """
- 높은 모델 정확도 ≠ 현재 후보에 대한 높은 적용성
- 음성 AI 예측 ≠ 독성 부재
- 음성 NAM 결과 ≠ Reliable Negative
- Out-of-domain 예측 ≠ 신뢰 가능한 근거
- 명목농도 ≠ 표적부위 노출
- 하나의 근거 흐름 ≠ Weight of Evidence
- 특정 endpoint 대체 ≠ 전체 독성패키지 대체
- 자료 없음 ≠ 음성 근거
"""
        )
    else:
        st.markdown(
            """
- High model accuracy ≠ high applicability to the current candidate
- Negative AI prediction ≠ absence of toxicity
- Negative NAM result ≠ Reliable Negative
- Out-of-domain prediction ≠ reliable evidence
- Nominal concentration ≠ target-site exposure
- One evidence stream ≠ weight of evidence
- Replacement of one endpoint ≠ replacement of the entire toxicology package
- Missing evidence ≠ negative evidence
"""
        )



header()
page = sidebar()
status_strip()

if page == "overview":
    page_project_overview()
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


# --- NORA v0.4.3 regulatory-status notice ---
try:
    _nora_lang = language()
    st.divider()
    if _nora_lang == "en":
        st.caption(
            "Regulatory-status notice: R0–R5 Evidence Roles and ET-R001–ET-R015 role caps "
            "are NORA's conservative internal decision-support policies. They are not "
            "regulatory classifications, agency approvals, animal-test waivers, or guarantees "
            "of regulatory acceptance. FDA AI/NAM documents cited by NORA are draft and nonbinding "
            "unless explicitly identified otherwise in the verified reference registry."
        )
    else:
        st.caption(
            "규제 상태 고지: R0–R5 Evidence Role과 ET-R001–ET-R015 역할 상한은 "
            "NORA의 보수적 내부 의사결정 지원 정책입니다. 규제기관이 정한 법적 분류, "
            "승인, 동물시험 면제 또는 규제 수용 보장이 아닙니다. NORA가 인용하는 FDA "
            "AI/NAM 문서는 검증된 레퍼런스 레지스트리에 달리 표시되지 않는 한 초안이며 "
            "비구속적입니다."
        )
except Exception:
    pass
