from __future__ import annotations

from functools import partial
from pathlib import Path

import csv
import hashlib
import re
import io
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .evidence import DocumentRecord, EvidenceAssertion
from .i18n import assertion_field_label, localize_result, value_label
from .models import AssessmentInput, AssessmentResult

LIMITATION_TEXT = {
    "ko": (
        "본 결과는 초기 연구 및 의사결정 지원을 위한 규칙기반 prototype 평가입니다. "
        "제품 안전성, 동물시험 면제, 특정 규제기관 수용, CTA/IND 승인 또는 전체 독성시험 대체를 보증하지 않습니다. "
        "R4 및 R5의 실제 사용에는 독성전문가 검토와 좁게 정의된 Context of Use가 필요합니다."
    ),
    "en": (
        "This result is a rule-based prototype assessment for early research and decision support. "
        "It does not certify product safety, waive animal studies, guarantee acceptance by a regulatory authority, predict CTA/IND approval, "
        "or replace the full toxicology package. Real-world use of R4 or R5 requires toxicology-expert review and a narrowly defined Context of Use."
    ),
}

REPORT_LABELS = {
    "ko": {
        "title": "ToxiGuard NORA EarlyTox 한글 자문보고서",
        "subtitle": "AI/NAM 초기 독성근거 검증 자문보고서",
        "overview": "평가 개요",
        "project": "프로젝트",
        "candidate": "후보물질",
        "modality": "제품 Modality",
        "objective": "평가 목적",
        "question": "독성 질문",
        "endpoint": "대상 Endpoint",
        "role": "현재 Evidence Role",
        "animal": "동물사용 관련 권고",
        "uncertainty": "잔여 불확실성",
        "model_risk": "모델 위험",
        "evidence_confidence": "근거 신뢰도",
        "toxicity_direction": "독성 신호 방향",
        "prediction_reliability": "개별 AI 예측 신뢰성",
        "development_concern": "개발 우려",
        "ai_credibility": "AI 독성 신뢰성 프로파일",
        "dimensions": "통합 평가축",
        "result": "결과",
        "hard_gate": "Hard Gate",
        "status": "상태",
        "basis_impact": "근거와 영향",
        "advisory": "설명 가능한 자문",
        "observation": "관찰(Observation)",
        "interpretation": "해석(Interpretation)",
        "development": "개발상 의미",
        "recommendations": "권고사항",
        "gaps": "우선순위 Data Gap",
        "gap": "Gap",
        "criticality": "중요도",
        "description_effect_recommendation": "설명·영향·권고",
        "impact": "영향",
        "recommendation": "권고",
        "no_gaps": "자동 생성된 주요 Data Gap 없음",
        "reviewed_evidence": "승인된 Evidence Assertion",
        "field_value": "필드·값",
        "source": "출처",
        "excerpt": "근거 발췌",
        "no_reviewed": "전문가가 승인한 Evidence Assertion이 없습니다.",
        "documents": "문서 인벤토리",
        "no_documents": "업로드 문서 없음",
        "audit": "감사 추적",
        "assessment_time": "평가 시각(UTC)",
        "trace_review": "Traceability / Assertion / Expert",
        "document_count": "문서 수",
        "limitations": "사용 제한",
        "unspecified": "미지정",
        "not_entered": "미입력",
        "undefined": "미정의",
        "none": "없음",
        "evidence_segments": "근거 구간",
        "approved_evidence_none": "전문가가 승인한 Evidence Assertion 없음",
    },
    "en": {
        "title": "ToxiGuard NORA EarlyTox Advisory Report",
        "subtitle": "AI/NAM Early-Toxicity Evidence Assurance Report",
        "overview": "Assessment Overview",
        "project": "Project",
        "candidate": "Candidate",
        "modality": "Product Modality",
        "objective": "Assessment Objective",
        "question": "Toxicity Question",
        "endpoint": "Target Endpoint",
        "role": "Current Evidence Role",
        "animal": "Animal-Use Recommendation",
        "uncertainty": "Residual Uncertainty",
        "model_risk": "Model Risk",
        "evidence_confidence": "Evidence Confidence",
        "toxicity_direction": "Toxicity Direction",
        "prediction_reliability": "Individual Prediction Reliability",
        "development_concern": "Development Concern",
        "ai_credibility": "AI Toxicity Credibility Profile",
        "dimensions": "Integrated Assessment Dimensions",
        "result": "Result",
        "hard_gate": "Hard Gates",
        "status": "Status",
        "basis_impact": "Rationale and Impact",
        "advisory": "Explainable Advisory",
        "observation": "Observation",
        "interpretation": "Interpretation",
        "development": "Development Relevance",
        "recommendations": "Recommendations",
        "gaps": "Priority Data Gaps",
        "gap": "Gap",
        "criticality": "Criticality",
        "description_effect_recommendation": "Description, Impact, and Recommendation",
        "impact": "Impact",
        "recommendation": "Recommendation",
        "no_gaps": "No major Data Gaps were generated automatically",
        "reviewed_evidence": "Reviewed Evidence Assertions",
        "field_value": "Field / Value",
        "source": "Source",
        "excerpt": "Evidence Excerpt",
        "no_reviewed": "No Evidence Assertions have been reviewed and accepted by an expert.",
        "documents": "Document Inventory",
        "no_documents": "No uploaded documents",
        "audit": "Audit Trail",
        "assessment_time": "Assessment Time (UTC)",
        "trace_review": "Traceability / Assertion Review / Expert Review",
        "document_count": "Document Count",
        "limitations": "Limitations",
        "unspecified": "Unspecified",
        "not_entered": "Not entered",
        "undefined": "Not defined",
        "none": "None",
        "evidence_segments": "evidence segments",
        "approved_evidence_none": "No reviewed Evidence Assertions",
    },
}


def _labels(language: str) -> dict[str, str]:
    return REPORT_LABELS["en" if language == "en" else "ko"]


def build_markdown_report(
    inp: AssessmentInput,
    result: AssessmentResult,
    assertions: Iterable[EvidenceAssertion] | None = None,
    documents: Iterable[DocumentRecord] | None = None,
    project_name: str = "",
    language: str = "ko",
) -> str:
    language = "en" if language == "en" else "ko"
    labels = _labels(language)
    localized = localize_result(result, inp, language)
    assertions = list(assertions or [])
    documents = list(documents or [])

    gap_lines = "\n".join(
        f"- **{gap['code']} · {gap['title']}** — {gap['description']}  \n  {labels['impact']}: {gap['effect']}  \n  {labels['recommendation']}: {gap['recommendation']}"
        for gap in localized["data_gaps"]
    ) or f"- {labels['no_gaps']}"
    gate_lines = "\n".join(
        f"- **{gate['gate']}: {gate['status']}** — {gate['rationale']} ({gate['effect']})"
        for gate in localized["gates"]
    )
    ai_profile_lines = "\n".join(f"- **{name}:** {value}" for name, value in localized["ai_credibility_profile"].items())
    ai_profile_labels = set(localized["ai_credibility_profile"].keys())
    score_lines = "\n".join(
        f"- **{name}:** {value}" for name, value in localized["scores"].items() if name not in ai_profile_labels
    )
    obs_lines = "\n".join(f"- {item}" for item in localized["observations"])
    int_lines = "\n".join(f"- {item}" for item in localized["interpretations"])
    rel_lines = "\n".join(f"- {item}" for item in localized["development_relevance"])
    rec_lines = "\n".join(f"- {item}" for item in localized["recommendations"])

    accepted = [item for item in assertions if item.review_status in {"승인", "수정"}]
    evidence_lines = "\n".join(
        f"- **{assertion_field_label(item, language)}: {value_label(item.proposed_value, language)}** — {item.source_document_name}, {item.source_location}  \n  `{item.source_excerpt[:280]}`"
        for item in accepted
    ) or f"- {labels['approved_evidence_none']}"
    document_lines = "\n".join(
        f"- {item.name} ({item.extension or item.media_type}) — {len(item.segments)} {labels['evidence_segments']}, SHA-256 {item.sha256[:16]}"
        for item in documents
    ) or f"- {labels['no_documents']}"

    return f"""# {labels['title']}

## 1. {labels['overview']}

- **{labels['project']}:** {project_name or labels['unspecified']}
- **{labels['candidate']}:** {inp.product.product_name or labels['not_entered']}
- **{labels['modality']}:** {value_label(inp.product.modality, language)}
- **{labels['objective']}:** {value_label(inp.context_of_use.objective, language)}
- **{labels['question']}:** {inp.context_of_use.question_of_interest or labels['undefined']}
- **{labels['endpoint']}:** {value_label(inp.context_of_use.target_endpoint, language)}
- **{labels['role']}:** **{localized['evidence_role_code']} — {localized['evidence_role_name']}**
- **{labels['animal']}:** {localized['animal_use_status']}
- **{labels['evidence_confidence']}:** {localized['evidence_confidence']}
- **{labels['toxicity_direction']}:** {localized['toxicity_direction']}
- **{labels['prediction_reliability']}:** {localized['prediction_reliability']}
- **{labels['development_concern']}:** {localized['development_concern']}
- **{labels['uncertainty']}:** {localized['residual_uncertainty']}
- **{labels['model_risk']}:** {localized['model_risk']}

> {localized['evidence_role_description']}

## 2. {labels['ai_credibility']}

{ai_profile_lines}

> {("모델 전체 성능과 현재 후보에 대한 개별 예측 신뢰성은 다릅니다. Data leakage, 부적절한 ground truth, out-of-domain 사용과 미보정 score는 높은 평균지표로 상쇄되지 않습니다." if language == "ko" else "Model-level performance and candidate-level prediction reliability are distinct. Data leakage, inadequate ground truth, out-of-domain use, and uncalibrated scores cannot be offset by a high average metric.")}

## 3. {labels['dimensions']}

{score_lines}

## 4. {labels['hard_gate']}

{gate_lines}

## 5. {labels['advisory']}

### {labels['observation']}
{obs_lines}

### {labels['interpretation']}
{int_lines}

### {labels['development']}
{rel_lines}

### {labels['recommendations']}
{rec_lines}

## 6. {labels['gaps']}

{gap_lines}

## 7. {labels['reviewed_evidence']}

{evidence_lines}

## 8. {labels['documents']}

{document_lines}

## 9. {labels['audit']}

- **Assessment ID:** {result.audit.get('assessment_id')}
- **{labels['assessment_time']}:** {result.audit.get('assessment_timestamp_utc')}
- **Ontology:** {result.audit.get('ontology_version')}
- **Rule Set:** {result.audit.get('rule_set_version')}
- **Input Hash:** {result.audit.get('input_hash')}
- **AI Domain Status:** {result.audit.get('ai_domain_status')}
- **Evidence Traceability:** {result.audit.get('evidence_traceable')}
- **Assertion Review:** {result.audit.get('assertions_reviewed')}
- **Expert Review:** {result.audit.get('expert_reviewed')}
- **Expert Note:** {result.audit.get('expert_review_note') or labels['none']}

## 10. {labels['limitations']}

{LIMITATION_TEXT[language]}
"""


def build_gap_csv(result: AssessmentResult, inp: AssessmentInput | None = None, language: str = "ko") -> bytes:
    language = "en" if language == "en" else "ko"
    localized = localize_result(result, inp or AssessmentInput(), language)
    stream = io.StringIO()
    writer = csv.writer(stream)
    if language == "en":
        writer.writerow(["Gap Code", "Title", "Description", "Criticality", "Rule ID", "Decision Impact", "Recommendation"])
    else:
        writer.writerow(["Gap Code", "제목", "설명", "중요도", "Rule ID", "판정 영향", "권고"])
    for gap in localized["data_gaps"]:
        writer.writerow([gap["code"], gap["title"], gap["description"], gap["criticality"], gap["rule_id"], gap["effect"], gap["recommendation"]])
    return stream.getvalue().encode("utf-8-sig")


def _register_fonts(language: str) -> tuple[str, str]:
    """Register a Korean/English-capable font when available.

    English reports may contain Korean project names or user-entered questions, so
    Helvetica alone is not a safe choice. Streamlit Cloud can install fonts-nanum
    through packages.txt; local installations fall back to standard PDF fonts.
    """
    regular_candidates = [
        Path("/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf"),
        Path("/usr/share/fonts/truetype/nanum/NanumGothic.ttf"),
        Path("/Library/Fonts/NanumBarunGothic.ttf"),
        Path.home() / "Library/Fonts/NanumBarunGothic.ttf",
    ]
    bold_candidates = [
        Path("/usr/share/fonts/truetype/nanum/NanumBarunGothicBold.ttf"),
        Path("/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"),
        Path("/Library/Fonts/NanumBarunGothicBold.ttf"),
        Path.home() / "Library/Fonts/NanumBarunGothicBold.ttf",
    ]
    regular = next((path for path in regular_candidates if path.exists()), None)
    bold = next((path for path in bold_candidates if path.exists()), regular)
    if regular:
        body_font = "NoraSans"
        heading_font = "NoraSans-Bold"
        try:
            pdfmetrics.getFont(body_font)
        except KeyError:
            pdfmetrics.registerFont(TTFont(body_font, str(regular)))
        try:
            pdfmetrics.getFont(heading_font)
        except KeyError:
            pdfmetrics.registerFont(TTFont(heading_font, str(bold or regular)))
        try:
            pdfmetrics.registerFontFamily(
                body_font,
                normal=body_font,
                bold=heading_font,
                italic=body_font,
                boldItalic=heading_font,
            )
        except Exception:
            pass
        return body_font, heading_font

    if language == "en":
        return "Helvetica", "Helvetica-Bold"
    body_font = "HYSMyeongJo-Medium"
    heading_font = "HYGothic-Medium"
    for font_name in (body_font, heading_font):
        try:
            pdfmetrics.getFont(font_name)
        except KeyError:
            pdfmetrics.registerFont(UnicodeCIDFont(font_name))
    return body_font, heading_font


def _p(text: object, style: ParagraphStyle) -> Paragraph:
    value = ("" if text is None else str(text)).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(value, style)


def _pm(text: object, style: ParagraphStyle) -> Paragraph:
    """Render code-authored line breaks and bold labels while escaping other markup."""
    value = "" if text is None else str(text)
    tokens = {"<br/>": "__NORA_BR__", "<br>": "__NORA_BR__", "<b>": "__NORA_B_OPEN__", "</b>": "__NORA_B_CLOSE__"}
    for token, placeholder in tokens.items():
        value = value.replace(token, placeholder)
    value = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    value = value.replace("__NORA_BR__", "<br/>").replace("__NORA_B_OPEN__", "<b>").replace("__NORA_B_CLOSE__", "</b>")
    return Paragraph(value, style)




def _stabilize_pdf_id(payload: bytes) -> bytes:
    """Replace ReportLab's run-specific trailer ID with a content-derived ID."""
    pattern = re.compile(rb"/ID\s*\n?\[<[^>]+><[^>]+>\]")
    placeholder = b"/ID\n[<00000000000000000000000000000000><00000000000000000000000000000000>]"
    canonical = pattern.sub(placeholder, payload, count=1)
    digest = hashlib.md5(canonical, usedforsecurity=False).hexdigest().encode("ascii")
    replacement = b"/ID\n[<" + digest + b"><" + digest + b">]"
    return pattern.sub(replacement, payload, count=1)

def build_pdf_report(
    inp: AssessmentInput,
    result: AssessmentResult,
    assertions: Iterable[EvidenceAssertion] | None = None,
    documents: Iterable[DocumentRecord] | None = None,
    project_name: str = "",
    language: str = "ko",
) -> bytes:
    language = "en" if language == "en" else "ko"
    labels = _labels(language)
    localized = localize_result(result, inp, language)
    assertions = list(assertions or [])
    documents = list(documents or [])
    body_font, heading_font = _register_fonts(language)
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=17 * mm,
        rightMargin=17 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=labels["title"],
        author="ToxiGuard NORA",
        invariant=1,
    )
    styles = getSampleStyleSheet()
    title = ParagraphStyle("NoraTitle", parent=styles["Title"], fontName=heading_font, fontSize=20, leading=25, textColor=colors.HexColor("#10243F"), alignment=TA_CENTER, spaceAfter=12)
    h1 = ParagraphStyle("NoraH1", parent=styles["Heading1"], fontName=heading_font, fontSize=13, leading=17, textColor=colors.HexColor("#173B63"), spaceBefore=10, spaceAfter=7)
    h2 = ParagraphStyle("NoraH2", parent=styles["Heading2"], fontName=heading_font, fontSize=11, leading=15, textColor=colors.HexColor("#176B87"), spaceBefore=7, spaceAfter=5)
    body = ParagraphStyle("NoraBody", parent=styles["BodyText"], fontName=body_font, fontSize=9, leading=13, textColor=colors.HexColor("#182230"), alignment=TA_LEFT, spaceAfter=4)
    small = ParagraphStyle("NoraSmall", parent=body, fontSize=7.7, leading=10.5, textColor=colors.HexColor("#52606D"))
    callout = ParagraphStyle("NoraCallout", parent=body, fontName=heading_font, fontSize=10.5, leading=15, textColor=colors.white, backColor=colors.HexColor("#10243F"), borderPadding=10, borderRadius=6, spaceAfter=12)

    story: list[object] = [
        _p("ToxiGuard NORA EarlyTox", title),
        _p(labels["subtitle"], h2),
        _pm(f"{localized['evidence_role_code']} — {localized['evidence_role_name']}<br/>{localized['evidence_role_description']}", callout),
    ]
    summary_rows = [
        [_p(labels["project"], body), _p(project_name or labels["unspecified"], body)],
        [_p(labels["candidate"], body), _p(inp.product.product_name or labels["not_entered"], body)],
        [_p(labels["modality"], body), _p(value_label(inp.product.modality, language), body)],
        [_p(labels["question"], body), _p(inp.context_of_use.question_of_interest or labels["undefined"], body)],
        [_p(labels["animal"], body), _p(localized["animal_use_status"], body)],
        [_p(labels["evidence_confidence"], body), _p(localized["evidence_confidence"], body)],
        [_p(labels["toxicity_direction"], body), _p(localized["toxicity_direction"], body)],
        [_p(labels["prediction_reliability"], body), _p(localized["prediction_reliability"], body)],
        [_p(labels["development_concern"], body), _p(localized["development_concern"], body)],
        [_p(labels["uncertainty"], body), _p(localized["residual_uncertainty"], body)],
        [_p(labels["model_risk"], body), _p(localized["model_risk"], body)],
    ]
    summary_table = Table(summary_rows, colWidths=[42 * mm, 131 * mm])
    summary_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9E2EA")), ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EFF7FB")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.extend([_p(f"1. {labels['overview']}", h1), summary_table, Spacer(1, 6)])

    ai_rows = [[_p(labels["ai_credibility"], body), _p(labels["result"], body)]] + [
        [_p(name, body), _p(value, body)] for name, value in localized["ai_credibility_profile"].items()
    ]
    ai_table = Table(ai_rows, colWidths=[82 * mm, 91 * mm], repeatRows=1)
    ai_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F7F78")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9E2EA")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3FAF8")]), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    story.extend([_p(f"2. {labels['ai_credibility']}", h1), ai_table])

    ai_profile_labels = set(localized["ai_credibility_profile"].keys())
    integrated_scores = [(name, value) for name, value in localized["scores"].items() if name not in ai_profile_labels]
    score_rows = [[_p(labels["dimensions"], body), _p(labels["result"], body)]] + [[_p(name, body), _p(value, body)] for name, value in integrated_scores]
    score_table = Table(score_rows, colWidths=[82 * mm, 91 * mm], repeatRows=1)
    score_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173B63")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9E2EA")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    story.extend([_p(f"3. {labels['dimensions']}", h1), score_table])

    story.append(_p(f"4. {labels['hard_gate']}", h1))
    gate_rows = [[_p("Gate", body), _p(labels["status"], body), _p(labels["basis_impact"], body)]]
    for gate in localized["gates"]:
        gate_rows.append([_p(gate["gate"], small), _p(gate["status"], small), _p(f"{gate['rationale']} / {gate['effect']}", small)])
    gate_table = Table(gate_rows, colWidths=[42 * mm, 27 * mm, 104 * mm], repeatRows=1)
    gate_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173B63")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D9E2EA")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story.append(gate_table)

    story.append(_p(f"5. {labels['advisory']}", h1))
    for heading, items in ((labels["observation"], localized["observations"]), (labels["interpretation"], localized["interpretations"]), (labels["development"], localized["development_relevance"]), (labels["recommendations"], localized["recommendations"])):
        story.append(_p(heading, h2))
        for item in items:
            story.append(_p(f"• {item}", body))

    story.append(Spacer(1, 8))
    story.append(_p(f"6. {labels['gaps']}", h1))
    gap_rows = [[_p(labels["gap"], body), _p(labels["criticality"], body), _p(labels["description_effect_recommendation"], body)]]
    for gap in localized["data_gaps"]:
        gap_rows.append([_pm(f"{gap['code']}<br/>{gap['title']}", small), _p(gap["criticality"], small), _pm(f"{gap['description']}<br/><b>{labels['impact']}:</b> {gap['effect']}<br/><b>{labels['recommendation']}:</b> {gap['recommendation']}", small)])
    if len(gap_rows) == 1:
        gap_rows.append([_p(labels["none"], small), _p("-", small), _p(labels["no_gaps"], small)])
    gap_table = Table(gap_rows, colWidths=[42 * mm, 28 * mm, 103 * mm], repeatRows=1)
    gap_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173B63")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D9E2EA")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FFF9F0")]), ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    story.append(gap_table)

    accepted = [item for item in assertions if item.review_status in {"승인", "수정"}]
    story.append(_p(f"7. {labels['reviewed_evidence']}", h1))
    if accepted:
        evidence_rows = [[_p(labels["field_value"], body), _p(labels["source"], body), _p(labels["excerpt"], body)]]
        for item in accepted:
            evidence_rows.append([_pm(f"{assertion_field_label(item, language)}<br/>{value_label(item.proposed_value, language)}", small), _pm(f"{item.source_document_name}<br/>{item.source_location}", small), _p(item.source_excerpt[:420], small)])
        evidence_table = Table(evidence_rows, colWidths=[42 * mm, 45 * mm, 86 * mm], repeatRows=1)
        evidence_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#176B87")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D9E2EA")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
        story.append(evidence_table)
    else:
        story.append(_p(labels["no_reviewed"], body))

    story.append(_p(f"8. {labels['audit']}", h1))
    audit_rows = [
        [_p("Assessment ID", small), _p(result.audit.get("assessment_id"), small)],
        [_p(labels["assessment_time"], small), _p(result.audit.get("assessment_timestamp_utc"), small)],
        [_p("Ontology / Rule Set", small), _p(f"{result.audit.get('ontology_version')} / {result.audit.get('rule_set_version')}", small)],
        [_p("Input Hash", small), _p(result.audit.get("input_hash"), small)],
        [_p("AI Domain", small), _p(result.audit.get("ai_domain_status"), small)],
        [_p(labels["trace_review"], small), _p(f"{result.audit.get('evidence_traceable')} / {result.audit.get('assertions_reviewed')} / {result.audit.get('expert_reviewed')}", small)],
        [_p(labels["document_count"], small), _p(len(documents), small)],
    ]
    audit_table = Table(audit_rows, colWidths=[55 * mm, 118 * mm])
    audit_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D9E2EA")), ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EFF7FB")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story.append(audit_table)
    story.extend([_p(f"9. {labels['limitations']}", h1), _p(LIMITATION_TEXT[language], small)])
    document.build(story, canvasmaker=partial(pdf_canvas.Canvas, invariant=1))
    return _stabilize_pdf_id(buffer.getvalue())
