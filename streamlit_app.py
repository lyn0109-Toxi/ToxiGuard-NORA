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
@media(max-width:1000px){.pipeline{grid-template-columns:repeat(3,1fr)}.status-strip{grid-template-columns:repeat(2,1fr)}}
@media(max-width:650px){.pipeline{grid-template-columns:1fr}.status-strip{grid-template-columns:1fr}}
</style>
""",
    unsafe_allow_html=True,
)


NAV_PAGES = [
    "프로젝트 개요",
    "문서 근거",
    "근거 검토",
    "평가 입력",
    "결과·보고서",
    "규칙·온톨로지",
]


@st.cache_resource
def get_store() -> ProjectStore:
    data_dir = Path(os.environ.get("NORA_DATA_DIR", APP_ROOT / ".nora_data"))
    return ProjectStore(data_dir / "projects.db")


def project() -> ProjectBundle:
    if "nora_project" not in st.session_state:
        st.session_state.nora_project = ProjectBundle.new()
    return st.session_state.nora_project


def set_project(value: ProjectBundle, page: str = "프로젝트 개요") -> None:
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
    st.markdown(
        """
<div class="nora-header">
  <h1>ToxiGuard NORA EarlyTox</h1>
  <p>AI와 비동물시험법(NAM)의 독성근거가 현재 후보물질의 개발에 어디까지 사용 가능한지 검증하는 한국어 Evidence Assurance 앱</p>
</div>
<div class="nora-banner">
  <strong>시험을 대체하기 전에, 대체 근거부터 검증합니다.</strong><br>
  AI는 근거를 구조화하고, 규칙엔진은 근거 역할과 Data Gap을 분류하며, 동물시험 축소·대체와 같은 고영향 결론은 독성전문가가 검토합니다.
</div>
""",
        unsafe_allow_html=True,
    )


def status_strip() -> None:
    p = project()
    counts = _status_counts()
    current = result()
    role = current.evidence_role_code if current else "미평가"
    st.markdown(
        f"""
<div class="status-strip">
  <div class="status-box"><span>프로젝트</span><strong>{p.project_name}</strong></div>
  <div class="status-box"><span>문서</span><strong>{len(p.documents)}개</strong></div>
  <div class="status-box"><span>Evidence Assertion</span><strong>{len(p.assertions)}개</strong></div>
  <div class="status-box"><span>승인·수정</span><strong>{counts.get('승인',0)+counts.get('수정',0)}개</strong></div>
  <div class="status-box"><span>현재 Evidence Role</span><strong>{role}</strong></div>
</div>
""",
        unsafe_allow_html=True,
    )


def pipeline() -> None:
    st.markdown(
        """
<div class="pipeline">
  <div class="pipe-step"><strong>1. 문서</strong>AI/NAM/PK 보고서</div>
  <div class="pipe-step"><strong>2. 추출</strong>출처연결 Assertion</div>
  <div class="pipe-step"><strong>3. 검토</strong>승인·수정·거절</div>
  <div class="pipe-step"><strong>4. 검증</strong>Gate·Data Gap</div>
  <div class="pipe-step"><strong>5. 판단</strong>Evidence Role R0-R5</div>
  <div class="pipe-step"><strong>6. 자문</strong>다음 근거·3Rs 권고</div>
</div>
""",
        unsafe_allow_html=True,
    )


def sidebar() -> str:
    p = project()
    with st.sidebar:
        st.markdown("## NORA EarlyTox")
        st.caption(f"NORA v{__version__} · {__ontology_version__} · 초기 간독성 vertical slice")

        with st.expander("프로젝트 관리", expanded=True):
            name = st.text_input("프로젝트명", value=p.project_name, key=f"project_name_{p.project_id}")
            owner = st.text_input("프로젝트 책임자", value=p.owner, key=f"project_owner_{p.project_id}")
            description = st.text_area("프로젝트 설명", value=p.description, height=75, key=f"project_desc_{p.project_id}")
            if st.button("메타데이터 반영", use_container_width=True, key=f"meta_apply_{p.project_id}"):
                p.project_name, p.owner, p.description = name.strip() or p.project_name, owner.strip(), description.strip()
                p.touch()
                add_event("프로젝트 메타데이터 수정", p.project_name)
                st.success("프로젝트 정보를 반영했습니다.")

            c1, c2 = st.columns(2)
            if c1.button("새 프로젝트", use_container_width=True):
                set_project(ProjectBundle.new(), "프로젝트 개요")
                st.rerun()
            if c2.button("로컬 저장", use_container_width=True):
                try:
                    add_event("로컬 프로젝트 저장", str(get_store().path))
                    get_store().save(p)
                    st.success("SQLite 프로젝트 보관함에 저장했습니다.")
                except Exception as exc:
                    st.error(f"저장 실패: {exc}")

            saved = get_store().list_projects()
            saved_map = {f"{item['project_name']} · {item['updated_at_utc'][:16]}": item["project_id"] for item in saved}
            selected_saved = st.selectbox("저장된 프로젝트", ["선택하지 않음"] + list(saved_map), key="saved_project_selector")
            c3, c4 = st.columns(2)
            if c3.button("불러오기", use_container_width=True, disabled=selected_saved == "선택하지 않음"):
                loaded = get_store().load(saved_map[selected_saved])
                if loaded:
                    loaded.add_event("로컬 프로젝트 불러오기", loaded.project_name)
                    set_project(loaded)
                    st.rerun()
            if c4.button("삭제", use_container_width=True, disabled=selected_saved == "선택하지 않음"):
                get_store().delete(saved_map[selected_saved])
                st.success("로컬 보관함에서 삭제했습니다.")
                st.rerun()

            project_upload = st.file_uploader("프로젝트 JSON 불러오기", type=["json"], key=f"project_json_{p.project_id}")
            if project_upload and st.button("JSON 프로젝트 적용", use_container_width=True, key=f"project_json_apply_{p.project_id}"):
                try:
                    loaded = load_project_json(project_upload.getvalue())
                    loaded.add_event("JSON 프로젝트 불러오기", project_upload.name)
                    set_project(loaded)
                    st.rerun()
                except Exception as exc:
                    st.error(f"프로젝트 JSON 오류: {exc}")

            st.download_button(
                "현재 프로젝트 JSON",
                project_json_bytes(p),
                file_name=f"{p.project_name.replace(' ','_')}.nora.json",
                mime="application/json",
                use_container_width=True,
            )

        with st.expander("Golden Case", expanded=False):
            demo = st.selectbox("가상 사례", list(CASE_BUILDERS), key="demo_selector")
            if st.button("사례 불러오기", use_container_width=True):
                demo_project = ProjectBundle.new(name=demo)
                demo_project.assessment_input = load_case(demo)
                demo_project.add_event("Golden Case 불러오기", demo)
                set_project(demo_project, "평가 입력")
                st.rerun()

        page = st.radio("작업공간", NAV_PAGES, key="nav_page")
        st.divider()
        st.caption("연구·의사결정 지원용 prototype입니다. 제품 안전성, 동물시험 면제 또는 규제기관 수용을 보장하지 않습니다.")
    return page


def page_project_overview() -> None:
    p = project()
    st.subheader("프로젝트 개요")
    st.write("AI/NAM 독성근거를 단순 점수로 평가하지 않고, 방법·실행·후보 적용성·사람 관련성·노출 번역·근거 일치성을 분리해 검토합니다.")
    pipeline()

    left, right = st.columns([1.12, 0.88], gap="large")
    with left:
        st.markdown("### 현재 개발 질문")
        cou = p.assessment_input.context_of_use
        if cou.question_of_interest:
            st.info(cou.question_of_interest)
        else:
            st.warning("Question of Interest가 아직 정의되지 않았습니다. ‘평가 입력’에서 먼저 정의하십시오.")
        table = [
            {"항목": "평가 목적", "현재 값": cou.objective},
            {"항목": "개발 단계", "현재 값": cou.development_stage},
            {"항목": "Endpoint", "현재 값": cou.target_endpoint},
            {"항목": "희망 Evidence Role", "현재 값": cou.intended_evidence_role},
            {"항목": "관할·맥락", "현재 값": cou.jurisdiction},
        ]
        st.dataframe(pd.DataFrame(table), hide_index=True, use_container_width=True)

        st.markdown("### 제품 맥락")
        product = p.assessment_input.product
        product_rows = [
            {"항목": "후보물질", "현재 값": product.product_name or "미입력"},
            {"항목": "Modality", "현재 값": product.modality},
            {"항목": "표적·기전", "현재 값": product.target_mechanism or "미입력"},
            {"항목": "전달체·제형", "현재 값": product.carrier_formulation or "미입력"},
            {"항목": "경로·노출", "현재 값": f"{product.route} / {product.exposure_pattern}"},
        ]
        st.dataframe(pd.DataFrame(product_rows), hide_index=True, use_container_width=True)

    with right:
        st.markdown("### 앱이 내리는 판단")
        for code, title, description in ROLE_DEFINITIONS.values():
            st.markdown(f"**{code} · {title}**  \n{description}")
        st.markdown("### 앱이 내리지 않는 판단")
        st.error("안전성 인증 · 동물시험 면제 · 규제기관 승인 예측 · 전체 독성패키지 대체")

    st.markdown("### 빠른 시작")
    q1, q2, q3 = st.columns(3)
    if q1.button("문서 업로드로 시작", use_container_width=True):
        st.session_state.nav_page = "문서 근거"
        st.rerun()
    if q2.button("수동 평가 입력", use_container_width=True):
        st.session_state.nav_page = "평가 입력"
        st.rerun()
    if q3.button("GP-L-CT 사례", use_container_width=True):
        demo_project = ProjectBundle.new(name="GP-L-CT EarlyTox")
        demo_project.assessment_input = load_case("GP-L-CT — 적용범위 밖 음성예측")
        set_project(demo_project, "평가 입력")
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
    st.subheader("문서 근거 작업공간")
    st.caption("PDF, DOCX, TXT/MD, CSV, XLSX/XLSM, JSON을 업로드하면 페이지·문단·시트·행 위치를 보존한 근거 구간을 생성합니다. 스캔 PDF OCR은 현재 포함하지 않습니다.")

    upload = st.file_uploader(
        "AI 모델 카드, NAM 보고서, PK/TK, biodistribution 또는 기존 독성자료",
        type=["pdf", "docx", "txt", "md", "csv", "xlsx", "xlsm", "json"],
        accept_multiple_files=True,
        key=f"doc_upload_{p.project_id}",
    )
    manual = st.text_area("직접 붙여넣을 근거 텍스트", height=125, key=f"manual_evidence_{p.project_id}", placeholder="모델 검증요약, NAM 결과, 대조군 및 노출정보 등을 붙여넣을 수 있습니다.")
    c1, c2 = st.columns([1, 1])
    if c1.button("선택 문서 처리", type="primary", use_container_width=True, disabled=not bool(upload)):
        with st.spinner("문서를 구조화하고 Evidence Assertion 후보를 추출하는 중입니다..."):
            added, skipped = _process_files(upload or [])
        st.success(f"문서 {added}개를 추가했습니다. 중복 {skipped}개는 제외했습니다.")
        st.rerun()
    if c2.button("붙여넣은 텍스트 추가", use_container_width=True, disabled=not manual.strip()):
        class ManualFile:
            name = "Manual_Evidence.txt"
            type = "text/plain"
            def getvalue(self_inner):
                return manual.encode("utf-8")
        added, skipped = _process_files([ManualFile()])
        st.success(f"수동 근거 {added}개를 추가했습니다.")
        st.rerun()

    if not p.documents:
        st.info("아직 업로드된 문서가 없습니다. 문서 없이 수동 입력만으로도 평가할 수 있지만, Evidence Role R4/R5에는 추적 가능한 근거가 중요합니다.")
        return

    st.markdown("### 문서 인벤토리")
    inventory = pd.DataFrame([document_inventory_row(item) for item in p.documents])
    st.dataframe(inventory, hide_index=True, use_container_width=True)

    selected_name = st.selectbox("문서 검토", [item.name for item in p.documents], key=f"selected_doc_{p.project_id}")
    selected = next(item for item in p.documents if item.name == selected_name)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("근거 구간", len(selected.segments))
    m2.metric("추출 문자", len(selected.extracted_text))
    m3.metric("자동 Assertion", sum(1 for item in p.assertions if item.source_document_id == selected.document_id))
    m4.metric("경고", len(selected.warnings))

    if selected.warnings:
        with st.expander("문서 처리 경고", expanded=True):
            for warning in selected.warnings:
                st.warning(warning)

    if selected.segments:
        location = st.selectbox("출처 위치", [segment.location for segment in selected.segments], key=f"segment_{selected.document_id}")
        segment = next(item for item in selected.segments if item.location == location)
        st.text_area("추출 텍스트", segment.text, height=330, disabled=True)

    d1, d2 = st.columns([1, 3])
    if d1.button("이 문서 삭제", use_container_width=True):
        p.documents = [item for item in p.documents if item.document_id != selected.document_id]
        p.assertions = [item for item in p.assertions if item.source_document_id != selected.document_id]
        add_event("문서 삭제", selected.name)
        invalidate_result()
        st.rerun()
    d2.caption("문서를 삭제하면 해당 문서에서 생성된 Assertion도 함께 제거됩니다.")


def page_assertion_review() -> None:
    p = project()
    st.subheader("Evidence Assertion 검토")
    st.caption("자동 추출값은 모두 ‘제안됨’ 상태입니다. 평가 입력에 반영하려면 사람이 승인·수정·거절해야 합니다.")

    if not p.assertions:
        st.info("검토할 Assertion이 없습니다. 먼저 문서를 업로드하거나 평가 입력을 수동으로 작성하십시오.")
        return

    counts = _status_counts()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("전체", len(p.assertions))
    c2.metric("제안됨", counts.get("제안됨", 0))
    c3.metric("승인·수정", counts.get("승인", 0) + counts.get("수정", 0))
    c4.metric("거절", counts.get("거절", 0))

    f1, f2, f3 = st.columns(3)
    categories = sorted({item.category for item in p.assertions})
    documents = sorted({item.source_document_name for item in p.assertions})
    selected_category = f1.selectbox("분류", ["전체"] + categories, key=f"assert_cat_{p.project_id}")
    selected_status = f2.selectbox("검토 상태", ["전체"] + REVIEW_STATUS_OPTIONS, key=f"assert_status_{p.project_id}")
    selected_document = f3.selectbox("출처 문서", ["전체"] + documents, key=f"assert_doc_{p.project_id}")
    search = st.text_input("검색", key=f"assert_search_{p.project_id}", placeholder="필드, 값, 발췌문 검색")

    filtered = []
    for item in p.assertions:
        if selected_category != "전체" and item.category != selected_category:
            continue
        if selected_status != "전체" and item.review_status != selected_status:
            continue
        if selected_document != "전체" and item.source_document_name != selected_document:
            continue
        haystack = f"{item.label_ko} {item.proposed_value} {item.source_excerpt}".lower()
        if search and search.lower() not in haystack:
            continue
        filtered.append(item)

    rows = assertion_table_rows(filtered)
    if not rows:
        st.warning("현재 필터에 해당하는 Assertion이 없습니다.")
        return
    frame = pd.DataFrame(rows)
    edited = st.data_editor(
        frame,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"assertion_editor_{p.project_id}_{selected_category}_{selected_status}_{selected_document}",
        disabled=[
            "Assertion ID", "분류", "평가 필드", "Field Path", "형식", "출처 문서", "출처 위치", "근거 발췌", "추출 신뢰도"
        ],
        column_config={
            "검토 상태": st.column_config.SelectboxColumn("검토 상태", options=REVIEW_STATUS_OPTIONS, required=True),
            "추출 신뢰도": st.column_config.NumberColumn("추출 신뢰도", min_value=0.0, max_value=1.0, format="%.2f"),
            "근거 발췌": st.column_config.TextColumn("근거 발췌", width="large"),
            "제안/수정 값": st.column_config.TextColumn("제안/수정 값", width="medium"),
            "검토 메모": st.column_config.TextColumn("검토 메모", width="medium"),
        },
    )

    b1, b2, b3 = st.columns(3)
    if b1.button("편집 내용 저장", type="primary", use_container_width=True):
        updated_subset = assertions_from_table_rows(edited.to_dict("records"), p.assertions)
        updated_by_id = {item.assertion_id: item for item in updated_subset}
        p.assertions = [updated_by_id.get(item.assertion_id, item) for item in p.assertions]
        add_event("Assertion 검토 저장", f"필터 결과 {len(updated_subset)}개")
        invalidate_result()
        st.success("검토상태와 수정값을 저장했습니다.")
        st.rerun()
    if b2.button("필터 결과 모두 승인", use_container_width=True):
        ids = {item.assertion_id for item in filtered}
        for item in p.assertions:
            if item.assertion_id in ids:
                item.review_status = "승인"
        add_event("Assertion 일괄 승인", f"{len(ids)}개")
        invalidate_result()
        st.rerun()
    if b3.button("승인 근거를 평가 입력에 적용", use_container_width=True):
        p.assessment_input = apply_reviewed_assertions(p.assessment_input, p.assertions)
        add_event("승인 Assertion 적용", f"승인·수정 {sum(1 for item in p.assertions if item.review_status in {'승인','수정'})}개")
        invalidate_result()
        st.success("승인된 근거를 구조화된 평가 입력에 반영했습니다.")
        st.session_state.nav_page = "평가 입력"
        st.rerun()

    with st.expander("평가에 반영되는 근거 원칙"):
        st.markdown(
            """
- `제안됨`: AI 또는 규칙기반 추출 후보이며 평가에 사용하지 않음
- `승인`: 출처와 값이 맞다고 사람이 확인
- `수정`: 사람이 값을 수정한 후 평가에 사용
- `거절`: 잘못된 추출이므로 사용하지 않음
- R4/R5에는 단순 문서 존재가 아니라 **출처 위치가 연결된 승인 Assertion과 전문가 검토**가 필요
"""
        )


def _assessment_form() -> AssessmentInput | None:
    p = project()
    current = p.assessment_input
    prefix = p.project_id

    with st.form(f"assessment_form_{prefix}"):
        tabs = st.tabs(["Context of Use", "제품·노출", "AI Model Card", "NAM Assay Card", "보조근거·Governance"])

        with tabs[0]:
            c1, c2, c3 = st.columns(3)
            objective = c1.selectbox(
                "평가 목적",
                ["AI 독성예측 결과 검증", "NAM 결과의 사람 관련성 평가", "AI·NAM·기존 근거 통합", "동물시험 범위 축소 가능성 평가", "특정 독성시험 대체 후보 평가"],
                index=["AI 독성예측 결과 검증", "NAM 결과의 사람 관련성 평가", "AI·NAM·기존 근거 통합", "동물시험 범위 축소 가능성 평가", "특정 독성시험 대체 후보 평가"].index(current.context_of_use.objective),
            )
            stage_options = ["탐색 연구", "후보물질 선정", "초기 비임상 개발", "IND/CTA 준비"]
            development_stage = c2.selectbox("개발 단계", stage_options, index=stage_options.index(current.context_of_use.development_stage))
            endpoint_options = ["초기 간독성", "신독성", "심장독성", "면역독성", "유전독성"]
            target_endpoint = c3.selectbox("대상 Endpoint", endpoint_options, index=endpoint_options.index(current.context_of_use.target_endpoint))
            question = st.text_area("Question of Interest", value=current.context_of_use.question_of_interest, height=110)
            r1, r2, r3 = st.columns(3)
            role_options = ["R1 · 가설 생성", "R2 · 초기 선별", "R3 · 보조 근거", "R4 · 동물시험 축소 지원", "R5 · 특정 시험 대체 후보"]
            intended_role = r1.selectbox("의도한 Evidence Role", role_options, index=role_options.index(current.context_of_use.intended_evidence_role))
            jurisdiction_options = ["연구용 / 내부 의사결정", "미국 FDA 사전미팅 준비", "유럽 EMA Scientific Advice 준비", "CTA/IND 근거 패키지 준비"]
            jurisdiction = r2.selectbox("관할·규제 맥락", jurisdiction_options, index=jurisdiction_options.index(current.context_of_use.jurisdiction))
            decision_owner = r3.text_input("의사결정 책임자", value=current.context_of_use.decision_owner)
            risk1, risk2 = st.columns(2)
            model_influence = risk1.slider("AI/NAM 결과의 의사결정 영향", 1, 5, int(current.context_of_use.model_influence))
            decision_consequence = risk2.slider("오판 시 결과의 심각성", 1, 5, int(current.context_of_use.decision_consequence))

        with tabs[1]:
            p1, p2, p3 = st.columns(3)
            product_name = p1.text_input("후보물질명", value=current.product.product_name)
            modality_options = ["저분자 NME", "올리고뉴클레오타이드", "siRNA 치료제", "나노의약품", "siRNA + 나노의약품", "바이오의약품", "유전자치료제"]
            modality = p2.selectbox("제품 Modality", modality_options, index=modality_options.index(current.product.modality))
            indication = p3.text_input("적응증", value=current.product.indication)
            p4, p5, p6 = st.columns(3)
            active_substance = p4.text_input("유효성분·서열", value=current.product.active_substance)
            target_mechanism = p5.text_input("표적·작용기전", value=current.product.target_mechanism)
            carrier_formulation = p6.text_input("전달체·제형", value=current.product.carrier_formulation)
            p7, p8, p9 = st.columns(3)
            route_options = ["경구", "정맥투여", "근육주사", "피하주사", "흡입", "국소"]
            route = p7.selectbox("투여경로", route_options, index=route_options.index(current.product.route))
            exposure_options = ["단회 노출", "반복 노출", "지속 노출"]
            exposure_pattern = p8.selectbox("노출 형태", exposure_options, index=exposure_options.index(current.product.exposure_pattern))
            planned_dose = p9.text_input("계획 용량", value=current.product.planned_dose)
            p10, p11, p12 = st.columns(3)
            frequency = p10.text_input("투여빈도", value=current.product.frequency)
            treatment_duration = p11.text_input("투여기간", value=current.product.treatment_duration)
            target_organs = p12.text_input("예상 표적장기", value=current.product.target_organs)
            p13, p14, p15, p16 = st.columns(4)
            human_cmax = p13.text_input("예상 Cmax", value=current.product.human_cmax)
            human_auc = p14.text_input("예상 AUC", value=current.product.human_auc)
            distribution_options = ["없음", "정성적 자료", "정량적 자료"]
            distribution_status = p15.selectbox("Biodistribution", distribution_options, index=distribution_options.index(current.product.distribution_status))
            rep_options = ["불명확", "부분적으로 확인", "임상제품 대표성 확인"]
            representativeness = p16.selectbox("시험물질 대표성", rep_options, index=rep_options.index(current.product.test_article_representativeness))

        with tabs[2]:
            use_ai = st.checkbox("AI/in silico 근거 사용", value=current.ai_model.use_ai)
            a1, a2, a3 = st.columns(3)
            model_name = a1.text_input("모델명", value=current.ai_model.model_name)
            model_version = a2.text_input("모델 버전", value=current.ai_model.model_version)
            model_type_options = ["Rule-based QSAR", "Statistical QSAR", "Machine learning classifier", "Deep learning / GNN", "Transcriptomic signature model"]
            model_type = a3.selectbox("모델 유형", model_type_options, index=model_type_options.index(current.ai_model.model_type))
            a4, a5, a6 = st.columns(3)
            ai_endpoint = a4.selectbox("예측 Endpoint", endpoint_options, index=endpoint_options.index(current.ai_model.endpoint))
            result_options = ["음성 / 낮은 위험 예측", "양성 / 위험 신호", "경계 / 불확실"]
            ai_result = a5.selectbox("AI 예측 결과", result_options, index=result_options.index(current.ai_model.result))
            ai_probability = a6.text_input("예측 확률(%)", value="" if current.ai_model.probability_percent is None else str(current.ai_model.probability_percent))
            domain_modalities = st.multiselect("학습·검증자료 Modality", ["저분자", "올리고뉴클레오타이드", "나노의약품", "바이오의약품"], default=current.ai_model.domain_modalities)
            a7, a8, a9, a10 = st.columns(4)
            ext_options = ["확인됨", "부분적으로 확인", "없음", "불명확"]
            external_validation = a7.selectbox("외부 독립검증", ext_options, index=ext_options.index(current.ai_model.external_validation))
            sensitivity = a8.text_input("Sensitivity (%)", value="" if current.ai_model.sensitivity_percent is None else str(current.ai_model.sensitivity_percent))
            specificity = a9.text_input("Specificity (%)", value="" if current.ai_model.specificity_percent is None else str(current.ai_model.specificity_percent))
            fnr = a10.text_input("False-negative rate (%)", value="" if current.ai_model.false_negative_rate_percent is None else str(current.ai_model.false_negative_rate_percent))
            a11, a12 = st.columns(2)
            cal_options = ["검증됨", "부분 검증", "미검증", "불명확"]
            calibration = a11.selectbox("확률 Calibration", cal_options, index=cal_options.index(current.ai_model.calibration_status))
            domain_options = ["자동 평가", "In-domain", "Borderline", "Out-of-domain", "Unknown"]
            domain_status = a12.selectbox("후보 Applicability Domain", domain_options, index=domain_options.index(current.ai_model.domain_status))
            ai_source = st.text_input("모델 출처", value=current.ai_model.source)
            known_limitations = st.text_area("알려진 한계", value=current.ai_model.known_limitations, height=85)

        with tabs[3]:
            use_nam = st.checkbox("사람 관련 NAM 근거 사용", value=current.nam_assay.use_nam)
            n1, n2, n3 = st.columns(3)
            nam_types = ["2D 세포시험", "공배양(Coculture)", "3D 간 Spheroid", "간 Organoid", "Liver-on-chip / MPS", "Omics 기반 시험"]
            nam_type = n1.selectbox("NAM 유형", nam_types, index=nam_types.index(current.nam_assay.nam_type))
            origin_options = ["사람 유래", "사람·동물 혼합", "동물 유래", "불명확"]
            system_origin = n2.selectbox("시험계 기원", origin_options, index=origin_options.index(current.nam_assay.system_origin))
            nam_result_options = ["음성", "양성", "경계", "시험 무효"]
            nam_result = n3.selectbox("NAM 결과", nam_result_options, index=nam_result_options.index(current.nam_assay.result))
            cell_types = st.multiselect("포함 세포", ["간세포(Hepatocyte)", "Kupffer cell", "Stellate cell", "간 내피세포", "담관세포"], default=current.nam_assay.cell_types)
            n4, n5, n6 = st.columns(3)
            metabolic_options = ["충분히 확인", "부분 확인", "확인되지 않음"]
            metabolic = n4.selectbox("대사능", metabolic_options, index=metabolic_options.index(current.nam_assay.metabolic_competence))
            immune_options = ["충분", "부분적", "미포함 / 불명확"]
            immune = n5.selectbox("면역반응 재현성", immune_options, index=immune_options.index(current.nam_assay.immune_competence))
            nam_exposure_options = ["단회/급성 노출", "반복노출", "지속노출"]
            nam_exposure = n6.selectbox("NAM 노출설계", nam_exposure_options, index=nam_exposure_options.index(current.nam_assay.exposure_design))
            n7, n8, n9, n10 = st.columns(4)
            control_options = ["유효", "실패", "없음 / 불명확"]
            positive_control = n7.selectbox("양성대조군", control_options, index=control_options.index(current.nam_assay.positive_control))
            negative_control = n8.selectbox("음성대조군", control_options, index=control_options.index(current.nam_assay.negative_control))
            carrier_options = ["포함", "미포함", "해당 없음"]
            carrier_control = n9.selectbox("Carrier-only", carrier_options, index=carrier_options.index(current.nam_assay.carrier_only_control))
            active_control = n10.selectbox("Active-only", carrier_options, index=carrier_options.index(current.nam_assay.active_only_control))
            n11, n12, n13, n14 = st.columns(4)
            protocol_options = ["완결", "부분적", "불충분"]
            protocol = n11.selectbox("프로토콜 완결성", protocol_options, index=protocol_options.index(current.nam_assay.protocol_completeness))
            measured_options = ["측정됨", "부분 측정", "측정 안 됨"]
            measured = n12.selectbox("Free/세포내 노출", measured_options, index=measured_options.index(current.nam_assay.measured_exposure))
            qivive_options = ["수행됨", "초기 연결", "없음"]
            qivive = n13.selectbox("QIVIVE/PBPK", qivive_options, index=qivive_options.index(current.nam_assay.qivive_pbpk))
            repro_options = ["Donor/lot/반복 재현성 확인", "일부 확인", "확인되지 않음"]
            reproducibility = n14.selectbox("재현성", repro_options, index=repro_options.index(current.nam_assay.reproducibility))
            nominal_exposure = st.text_input("명목 농도", value=current.nam_assay.nominal_exposure)
            nam_endpoints = st.multiselect("NAM Endpoint", ["Cell viability / ATP", "미토콘드리아 기능", "산화스트레스", "ALT / AST / GLDH", "Cytokine", "담즙산 수송", "CYP 대사기능", "Omics signature"], default=current.nam_assay.endpoints)

        with tabs[4]:
            e1, e2, e3 = st.columns(3)
            mechanistic = e1.checkbox("기전 기반 근거", value=current.supporting_evidence.mechanistic_evidence)
            class_evidence = e2.checkbox("동일계열·임상 Class 근거", value=current.supporting_evidence.class_or_clinical_evidence)
            quantitative_bio = e3.checkbox("정량적 Biodistribution", value=current.supporting_evidence.quantitative_biodistribution)
            e4, e5, e6 = st.columns(3)
            pk_tk = e4.checkbox("PK/TK 및 노출-반응", value=current.supporting_evidence.pk_tk_evidence)
            invivo = e5.checkbox("기존 in vivo 독성자료", value=current.supporting_evidence.existing_in_vivo_evidence)
            human_evidence = e6.checkbox("사람·임상·사람 조직 근거", value=current.supporting_evidence.human_evidence)
            g1, g2, g3, g4 = st.columns(4)
            traceable = g1.checkbox("근거 추적 가능", value=current.supporting_evidence.evidence_traceable)
            assertions_reviewed = g2.checkbox("Assertion 검토 완료", value=current.supporting_evidence.assertions_reviewed)
            expert_reviewed = g3.checkbox("독성전문가 검토 완료", value=current.supporting_evidence.expert_reviewed)
            version_locked = g4.checkbox("버전 기록 완료", value=current.supporting_evidence.version_locked)
            expert_note = st.text_area("전문가 검토 메모", value=current.supporting_evidence.expert_review_note, height=85)
            support_note = st.text_area("보조 근거 설명", value=current.supporting_evidence.supporting_note, height=100)

        submitted = st.form_submit_button("평가 입력 저장", type="primary", use_container_width=True)

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
    st.subheader("구조화된 평가 입력")
    st.caption("승인된 Assertion을 자동 적용한 뒤 사람이 최종 입력값을 검토할 수 있습니다. 현재 상세 규칙의 활성 범위는 초기 간독성입니다.")
    updated = _assessment_form()
    if updated:
        project().assessment_input = updated
        project().touch()
        add_event("구조화 평가 입력 저장", updated.product.product_name or "후보 미입력")
        invalidate_result()
        st.success("평가 입력을 저장했습니다.")
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
    st.subheader("NORA 자문 결과 및 보고서")
    st.caption("평가 결과는 안전성 인증이 아니라, 현재 근거의 사용 가능한 역할과 다음 근거를 설명합니다.")

    if st.button("NORA EarlyTox 평가 실행", type="primary", use_container_width=True):
        _run_assessment()
        st.rerun()

    assessed = result()
    if not assessed:
        st.info("평가를 실행하면 Evidence Role, Hard Gate, Data Gap, 자문 및 내보내기 파일이 생성됩니다.")
        return

    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        st.markdown(
            f"""
<div class="role-card">
  <div class="small-muted" style="color:#cfe7ec">현재 Evidence Role</div>
  <div class="role-code">{assessed.evidence_role_code}</div>
  <div class="role-name">{assessed.evidence_role_name}</div>
  <div class="role-desc">{assessed.evidence_role_description}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    with right:
        st.markdown("### 동물사용 관련 권고")
        if assessed.evidence_role <= 2:
            st.error(assessed.animal_use_status)
        elif assessed.evidence_role == 3:
            st.warning(assessed.animal_use_status)
        else:
            st.success(assessed.animal_use_status)
        st.write(assessed.animal_use_description)
        st.metric("모델 위험", assessed.model_risk)
        st.metric("잔여 불확실성", assessed.residual_uncertainty)
        st.metric("독립 근거 흐름", assessed.evidence_stream_count)

    st.markdown("### 평가축")
    score_items = list(assessed.scores.items())
    columns = st.columns(3)
    for index, (label, value) in enumerate(score_items):
        with columns[index % 3]:
            _score_card(label, value)

    tabs = st.tabs(["Hard Gate", "Data Gap", "설명 가능한 자문", "Evidence Ledger", "Audit Trail"])
    with tabs[0]:
        for gate in assessed.gates:
            css = "gate-pass" if gate.status == "통과" else "gate-cond" if gate.status == "조건부" else "gate-fail"
            with st.container(border=True):
                st.markdown(f"<div class='{css}' style='padding-left:.75rem'><strong>{gate.gate} · {gate.status}</strong><br>{gate.rationale}<br><span class='small-muted'>영향: {gate.effect}</span></div>", unsafe_allow_html=True)
    with tabs[1]:
        if assessed.data_gaps:
            gap_frame = pd.DataFrame([gap.to_dict() for gap in assessed.data_gaps]).rename(
                columns={"code": "Gap Code", "title": "제목", "description": "설명", "criticality": "중요도", "rule_id": "Rule ID", "effect": "판정 영향", "recommendation": "권고"}
            )
            st.dataframe(gap_frame, hide_index=True, use_container_width=True)
        else:
            st.success("자동 생성된 주요 Data Gap이 없습니다. 실제 사용 전 전문가 검토가 필요합니다.")
    with tabs[2]:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 관찰")
            for item in assessed.observations:
                st.write(f"- {item}")
            st.markdown("#### 해석")
            for item in assessed.interpretations:
                st.write(f"- {item}")
        with c2:
            st.markdown("#### 개발상 의미")
            for item in assessed.development_relevance:
                st.write(f"- {item}")
            st.markdown("#### 권고사항")
            for item in assessed.recommendations:
                st.write(f"- {item}")
    with tabs[3]:
        accepted = [item for item in p.assertions if item.review_status in {"승인", "수정"}]
        if accepted:
            st.dataframe(pd.DataFrame(assertion_table_rows(accepted)), hide_index=True, use_container_width=True)
        else:
            st.info("승인된 Evidence Assertion이 없습니다. 수동 입력으로 평가한 경우에도 R4/R5 전에는 근거 추적성을 보완하십시오.")
    with tabs[4]:
        audit_rows = [event.to_dict() for event in reversed(p.audit_events)]
        st.dataframe(pd.DataFrame(audit_rows), hide_index=True, use_container_width=True)
        st.json(assessed.audit)

    st.markdown("### 다운로드")
    accepted = [item for item in p.assertions if item.review_status in {"승인", "수정"}]
    markdown = build_markdown_report(p.assessment_input, assessed, accepted, p.documents, p.project_name)
    jsonld = build_jsonld(p.assessment_input, assessed, accepted, p.documents, p.project_id, p.project_name)
    turtle = build_turtle(p.assessment_input, assessed, accepted, p.documents, p.project_id, p.project_name)
    try:
        pdf = build_pdf_report(p.assessment_input, assessed, accepted, p.documents, p.project_name)
        pdf_error = None
    except Exception as exc:
        pdf = b""
        pdf_error = str(exc)

    d1, d2, d3 = st.columns(3)
    d1.download_button("한글 자문보고서(MD)", markdown.encode("utf-8"), file_name=f"{p.project_name}_EarlyTox_Report.md", mime="text/markdown", use_container_width=True)
    d2.download_button("Ontology JSON-LD", json.dumps(jsonld, ensure_ascii=False, indent=2).encode("utf-8"), file_name=f"{p.project_name}_EarlyTox.jsonld", mime="application/ld+json", use_container_width=True)
    d3.download_button("Ontology Turtle", turtle.encode("utf-8"), file_name=f"{p.project_name}_EarlyTox.ttl", mime="text/turtle", use_container_width=True)
    d4, d5, d6 = st.columns(3)
    d4.download_button("Data Gap CSV", build_gap_csv(assessed), file_name=f"{p.project_name}_Data_Gaps.csv", mime="text/csv", use_container_width=True)
    d5.download_button("프로젝트 JSON", project_json_bytes(p), file_name=f"{p.project_name}.nora.json", mime="application/json", use_container_width=True)
    d6.download_button("한글 자문보고서(PDF)", pdf, file_name=f"{p.project_name}_EarlyTox_Report.pdf", mime="application/pdf", use_container_width=True, disabled=not bool(pdf))
    if pdf_error:
        st.warning(f"PDF 생성이 비활성화되었습니다: {pdf_error}")


def page_rules() -> None:
    st.subheader("규칙 카탈로그와 TG-PTO-ET")
    st.caption("OWL/RDF는 개념과 관계를 표현하고, SHACL은 필수정보와 추적성을 검증하며, 결정론적 Rule Engine이 Evidence Role과 Data Gap을 계산합니다.")
    st.code(
        "Product & Exposure → Toxicity Question → AI/NAM Context of Use → Credibility → Applicability → Human/Exposure Relevance → Concordance → Uncertainty → Evidence Role → 3Rs Recommendation",
        language="text",
    )
    with RULE_CATALOG_PATH.open("r", encoding="utf-8") as stream:
        rules = json.load(stream)
    st.markdown("### EarlyTox 규칙 카탈로그")
    st.dataframe(pd.DataFrame(rules), hide_index=True, use_container_width=True)

    t1, t2 = st.tabs(["OWL/RDF Core", "SHACL Shapes"])
    core_text = ONTOLOGY_CORE_PATH.read_text(encoding="utf-8")
    shape_text = ONTOLOGY_SHAPES_PATH.read_text(encoding="utf-8")
    with t1:
        st.code(core_text, language="turtle")
        st.download_button("TG-PTO-ET Core TTL", core_text.encode("utf-8"), file_name="tg_pto_et_core.ttl", mime="text/turtle")
    with t2:
        st.code(shape_text, language="turtle")
        st.download_button("TG-PTO-ET SHACL TTL", shape_text.encode("utf-8"), file_name="tg_pto_et_shapes.ttl", mime="text/turtle")

    st.markdown("### 최상위 논리제약")
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


header()
page = sidebar()
status_strip()

if page == "프로젝트 개요":
    page_project_overview()
elif page == "문서 근거":
    page_documents()
elif page == "근거 검토":
    page_assertion_review()
elif page == "평가 입력":
    page_assessment_input()
elif page == "결과·보고서":
    page_results()
elif page == "규칙·온톨로지":
    page_rules()
