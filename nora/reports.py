from __future__ import annotations

import csv
import io
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .evidence import DocumentRecord, EvidenceAssertion
from .models import AssessmentInput, AssessmentResult


LIMITATION_TEXT = (
    "본 결과는 초기 연구 및 의사결정 지원을 위한 규칙기반 prototype 평가입니다. "
    "제품 안전성, 동물시험 면제, 특정 규제기관 수용, CTA/IND 승인 또는 전체 독성시험 대체를 보증하지 않습니다. "
    "R4 및 R5의 실제 사용에는 독성전문가 검토와 좁게 정의된 Context of Use가 필요합니다."
)


def build_markdown_report(
    inp: AssessmentInput,
    result: AssessmentResult,
    assertions: Iterable[EvidenceAssertion] | None = None,
    documents: Iterable[DocumentRecord] | None = None,
    project_name: str = "",
) -> str:
    assertions = list(assertions or [])
    documents = list(documents or [])
    gap_lines = "\n".join(
        f"- **{gap.code} · {gap.title}** - {gap.description}  \n  영향: {gap.effect}  \n  권고: {gap.recommendation}"
        for gap in result.data_gaps
    ) or "- 자동 생성된 주요 데이터 갭 없음"

    gate_lines = "\n".join(
        f"- **{gate.gate}: {gate.status}** - {gate.rationale} ({gate.effect})"
        for gate in result.gates
    )
    score_lines = "\n".join(f"- **{name}:** {value}" for name, value in result.scores.items())
    obs_lines = "\n".join(f"- {item}" for item in result.observations)
    int_lines = "\n".join(f"- {item}" for item in result.interpretations)
    rel_lines = "\n".join(f"- {item}" for item in result.development_relevance)
    rec_lines = "\n".join(f"- {item}" for item in result.recommendations)

    accepted = [item for item in assertions if item.review_status in {"승인", "수정"}]
    evidence_lines = "\n".join(
        f"- **{item.label_ko}: {item.proposed_value}** - {item.source_document_name}, {item.source_location}  \n  `{item.source_excerpt[:280]}`"
        for item in accepted
    ) or "- 전문가가 승인한 Evidence Assertion 없음"
    document_lines = "\n".join(
        f"- {item.name} ({item.extension or item.media_type}) - {len(item.segments)}개 근거 구간, SHA-256 {item.sha256[:16]}"
        for item in documents
    ) or "- 업로드 문서 없음"

    return f"""# ToxiGuard NORA EarlyTox 한글 자문보고서

## 1. 평가 개요

- **프로젝트:** {project_name or '미지정'}
- **후보물질:** {inp.product.product_name or '미입력'}
- **제품 Modality:** {inp.product.modality}
- **평가 목적:** {inp.context_of_use.objective}
- **독성 질문:** {inp.context_of_use.question_of_interest or '미정의'}
- **대상 Endpoint:** {inp.context_of_use.target_endpoint}
- **현재 Evidence Role:** **{result.evidence_role_code} - {result.evidence_role_name}**
- **동물사용 관련 권고:** {result.animal_use_status}
- **잔여 불확실성:** {result.residual_uncertainty}
- **모델 위험:** {result.model_risk}

> {result.evidence_role_description}

## 2. 평가축

{score_lines}

## 3. Hard Gate

{gate_lines}

## 4. 설명 가능한 자문

### 관찰(Observation)
{obs_lines}

### 해석(Interpretation)
{int_lines}

### 개발상 의미
{rel_lines}

### 권고사항
{rec_lines}

## 5. 우선순위 Data Gap

{gap_lines}

## 6. 승인된 Evidence Assertion

{evidence_lines}

## 7. 문서 인벤토리

{document_lines}

## 8. 감사 추적

- **Assessment ID:** {result.audit.get('assessment_id')}
- **평가 시각(UTC):** {result.audit.get('assessment_timestamp_utc')}
- **Ontology:** {result.audit.get('ontology_version')}
- **Rule Set:** {result.audit.get('rule_set_version')}
- **Input Hash:** {result.audit.get('input_hash')}
- **AI Domain Status:** {result.audit.get('ai_domain_status')}
- **Evidence Traceability:** {result.audit.get('evidence_traceable')}
- **Assertion Review:** {result.audit.get('assertions_reviewed')}
- **Expert Review:** {result.audit.get('expert_reviewed')}
- **Expert Note:** {result.audit.get('expert_review_note') or '없음'}

## 9. 사용 제한

{LIMITATION_TEXT}
"""


def build_gap_csv(result: AssessmentResult) -> bytes:
    stream = io.StringIO()
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["Gap Code", "제목", "설명", "중요도", "Rule ID", "판정 영향", "권고"])
    for gap in result.data_gaps:
        writer.writerow(
            [
                gap.code,
                gap.title,
                gap.description,
                gap.criticality,
                gap.rule_id,
                gap.effect,
                gap.recommendation,
            ]
        )
    return stream.getvalue().encode("utf-8-sig")


def _register_korean_fonts() -> tuple[str, str]:
    body_font = "HYSMyeongJo-Medium"
    heading_font = "HYGothic-Medium"
    for font_name in (body_font, heading_font):
        try:
            pdfmetrics.getFont(font_name)
        except KeyError:
            pdfmetrics.registerFont(UnicodeCIDFont(font_name))
    return body_font, heading_font


def _invariant_canvas(*args, **kwargs) -> Canvas:
    """Build deterministic PDFs for versioned golden-case artifacts."""
    kwargs["invariant"] = 1
    return Canvas(*args, **kwargs)


def _p(text: object, style: ParagraphStyle) -> Paragraph:
    value = str(text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(value, style)


def build_pdf_report(
    inp: AssessmentInput,
    result: AssessmentResult,
    assertions: Iterable[EvidenceAssertion] | None = None,
    documents: Iterable[DocumentRecord] | None = None,
    project_name: str = "",
) -> bytes:
    assertions = list(assertions or [])
    documents = list(documents or [])
    body_font, heading_font = _register_korean_fonts()
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=17 * mm,
        rightMargin=17 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="ToxiGuard NORA EarlyTox 한글 자문보고서",
        author="ToxiGuard NORA",
    )

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "NoraTitle",
        parent=styles["Title"],
        fontName=heading_font,
        fontSize=20,
        leading=25,
        textColor=colors.HexColor("#10243F"),
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    h1 = ParagraphStyle(
        "NoraH1",
        parent=styles["Heading1"],
        fontName=heading_font,
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#173B63"),
        spaceBefore=10,
        spaceAfter=7,
    )
    h2 = ParagraphStyle(
        "NoraH2",
        parent=styles["Heading2"],
        fontName=heading_font,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#176B87"),
        spaceBefore=7,
        spaceAfter=5,
    )
    body = ParagraphStyle(
        "NoraBody",
        parent=styles["BodyText"],
        fontName=body_font,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#182230"),
        alignment=TA_LEFT,
        spaceAfter=4,
    )
    small = ParagraphStyle(
        "NoraSmall",
        parent=body,
        fontSize=7.7,
        leading=10.5,
        textColor=colors.HexColor("#52606D"),
    )
    callout = ParagraphStyle(
        "NoraCallout",
        parent=body,
        fontName=heading_font,
        fontSize=10.5,
        leading=15,
        textColor=colors.white,
        backColor=colors.HexColor("#10243F"),
        borderPadding=10,
        borderRadius=6,
        spaceAfter=12,
    )

    story: list[object] = [
        _p("ToxiGuard NORA EarlyTox", title),
        _p("AI/NAM 초기 독성근거 검증 한글 자문보고서", h2),
        _p(
            f"{result.evidence_role_code} - {result.evidence_role_name}<br/>{result.evidence_role_description}",
            callout,
        ),
    ]

    summary_rows = [
        [_p("프로젝트", body), _p(project_name or "미지정", body)],
        [_p("후보물질", body), _p(inp.product.product_name or "미입력", body)],
        [_p("제품 Modality", body), _p(inp.product.modality, body)],
        [_p("독성 질문", body), _p(inp.context_of_use.question_of_interest or "미정의", body)],
        [_p("동물사용 권고", body), _p(result.animal_use_status, body)],
        [_p("잔여 불확실성", body), _p(result.residual_uncertainty, body)],
        [_p("모델 위험", body), _p(result.model_risk, body)],
    ]
    summary_table = Table(summary_rows, colWidths=[38 * mm, 135 * mm])
    summary_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9E2EA")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EFF7FB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([_p("1. 평가 개요", h1), summary_table, Spacer(1, 6)])

    score_rows = [[_p("평가축", body), _p("결과", body)]] + [
        [_p(name, body), _p(value, body)] for name, value in result.scores.items()
    ]
    score_table = Table(score_rows, colWidths=[82 * mm, 91 * mm], repeatRows=1)
    score_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173B63")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9E2EA")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.extend([_p("2. 평가축", h1), score_table])

    story.append(_p("3. Hard Gate", h1))
    gate_rows = [[_p("Gate", body), _p("상태", body), _p("근거와 영향", body)]]
    for gate in result.gates:
        gate_rows.append(
            [
                _p(gate.gate, small),
                _p(gate.status, small),
                _p(f"{gate.rationale} / {gate.effect}", small),
            ]
        )
    gate_table = Table(gate_rows, colWidths=[40 * mm, 24 * mm, 109 * mm], repeatRows=1)
    gate_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173B63")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D9E2EA")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(gate_table)

    story.append(_p("4. 설명 가능한 자문", h1))
    for heading, items in (
        ("관찰(Observation)", result.observations),
        ("해석(Interpretation)", result.interpretations),
        ("개발상 의미", result.development_relevance),
        ("권고사항", result.recommendations),
    ):
        story.append(_p(heading, h2))
        for item in items:
            story.append(_p(f"• {item}", body))

    story.append(PageBreak())
    story.append(_p("5. 우선순위 Data Gap", h1))
    gap_rows = [[_p("Gap", body), _p("중요도", body), _p("설명·영향·권고", body)]]
    for gap in result.data_gaps:
        gap_rows.append(
            [
                _p(f"{gap.code}<br/>{gap.title}", small),
                _p(gap.criticality, small),
                _p(f"{gap.description}<br/><b>영향:</b> {gap.effect}<br/><b>권고:</b> {gap.recommendation}", small),
            ]
        )
    if len(gap_rows) == 1:
        gap_rows.append([_p("없음", small), _p("-", small), _p("자동 생성된 주요 Data Gap 없음", small)])
    gap_table = Table(gap_rows, colWidths=[40 * mm, 25 * mm, 108 * mm], repeatRows=1)
    gap_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173B63")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D9E2EA")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FFF9F0")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(gap_table)

    accepted = [item for item in assertions if item.review_status in {"승인", "수정"}]
    story.append(_p("6. 승인된 Evidence Assertion", h1))
    if accepted:
        evidence_rows = [[_p("필드·값", body), _p("출처", body), _p("근거 발췌", body)]]
        for item in accepted:
            evidence_rows.append(
                [
                    _p(f"{item.label_ko}<br/>{item.proposed_value}", small),
                    _p(f"{item.source_document_name}<br/>{item.source_location}", small),
                    _p(item.source_excerpt[:420], small),
                ]
            )
        evidence_table = Table(evidence_rows, colWidths=[42 * mm, 45 * mm, 86 * mm], repeatRows=1)
        evidence_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#176B87")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D9E2EA")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(evidence_table)
    else:
        story.append(_p("전문가가 승인한 Evidence Assertion이 없습니다.", body))

    story.append(_p("7. 감사 추적", h1))
    audit_rows = [
        [_p("Assessment ID", small), _p(result.audit.get("assessment_id"), small)],
        [_p("평가 시각(UTC)", small), _p(result.audit.get("assessment_timestamp_utc"), small)],
        [_p("Ontology / Rule Set", small), _p(f"{result.audit.get('ontology_version')} / {result.audit.get('rule_set_version')}", small)],
        [_p("Input Hash", small), _p(result.audit.get("input_hash"), small)],
        [_p("AI Domain", small), _p(result.audit.get("ai_domain_status"), small)],
        [_p("Traceability / Assertion / Expert", small), _p(f"{result.audit.get('evidence_traceable')} / {result.audit.get('assertions_reviewed')} / {result.audit.get('expert_reviewed')}", small)],
        [_p("문서 수", small), _p(len(documents), small)],
    ]
    audit_table = Table(audit_rows, colWidths=[48 * mm, 125 * mm])
    audit_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D9E2EA")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EFF7FB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(audit_table)
    story.extend([_p("8. 사용 제한", h1), _p(LIMITATION_TEXT, small)])

    document.build(story, canvasmaker=_invariant_canvas)
    return buffer.getvalue()
