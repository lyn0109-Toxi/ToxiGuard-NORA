from __future__ import annotations

import copy
import re
import uuid
from dataclasses import fields, is_dataclass
from typing import Any, Iterable

from .evidence import DocumentRecord, EvidenceAssertion, SourceSegment
from .models import AssessmentInput


REVIEWED_STATUSES = {"승인", "수정"}
REVIEW_STATUS_OPTIONS = ["제안됨", "승인", "수정", "거절"]


def _new_id() -> str:
    return f"AST-{uuid.uuid4().hex[:12]}"


def _excerpt(text: str, start: int, end: int, radius: int = 230) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    return re.sub(r"\s+", " ", text[left:right]).strip()


def _clean_value(value: str) -> str:
    value = re.sub(r"\s+", " ", value or "").strip(" \t\n\r;,.|-")
    return value[:220]


def _add(
    assertions: list[EvidenceAssertion],
    document: DocumentRecord,
    segment: SourceSegment,
    *,
    category: str,
    field_path: str,
    label_ko: str,
    proposed_value: str,
    value_type: str = "str",
    confidence: float = 0.75,
    match_span: tuple[int, int] | None = None,
) -> None:
    value = _clean_value(proposed_value)
    if not value:
        return
    key = (field_path, value.lower(), document.document_id)
    if any((item.field_path, item.proposed_value.lower(), item.source_document_id) == key for item in assertions):
        return
    start, end = match_span or (0, min(len(segment.text), 320))
    assertions.append(
        EvidenceAssertion(
            assertion_id=_new_id(),
            category=category,
            field_path=field_path,
            label_ko=label_ko,
            proposed_value=value,
            value_type=value_type,
            source_document_id=document.document_id,
            source_document_name=document.name,
            source_location=segment.location,
            source_excerpt=_excerpt(segment.text, start, end),
            confidence=round(max(0.0, min(1.0, confidence)), 2),
        )
    )


def _first_regex(
    assertions: list[EvidenceAssertion],
    document: DocumentRecord,
    segment: SourceSegment,
    pattern: str,
    *,
    category: str,
    field_path: str,
    label_ko: str,
    value_type: str = "str",
    confidence: float = 0.92,
    flags: int = re.IGNORECASE,
    transform: Any = None,
) -> None:
    match = re.search(pattern, segment.text, flags=flags)
    if not match:
        return
    value = match.group(1) if match.lastindex else match.group(0)
    if transform:
        value = transform(value)
    _add(
        assertions,
        document,
        segment,
        category=category,
        field_path=field_path,
        label_ko=label_ko,
        proposed_value=str(value),
        value_type=value_type,
        confidence=confidence,
        match_span=(match.start(), match.end()),
    )


def _keyword_assertion(
    assertions: list[EvidenceAssertion],
    document: DocumentRecord,
    segment: SourceSegment,
    *,
    patterns: Iterable[str],
    category: str,
    field_path: str,
    label_ko: str,
    proposed_value: str,
    value_type: str = "str",
    confidence: float = 0.72,
) -> None:
    for pattern in patterns:
        match = re.search(pattern, segment.text, flags=re.IGNORECASE)
        if match:
            _add(
                assertions,
                document,
                segment,
                category=category,
                field_path=field_path,
                label_ko=label_ko,
                proposed_value=proposed_value,
                value_type=value_type,
                confidence=confidence,
                match_span=(match.start(), match.end()),
            )
            return


def extract_assertions(document: DocumentRecord) -> list[EvidenceAssertion]:
    """Create source-linked, reviewable candidate assertions from one document.

    The extractor is deliberately conservative. It proposes structured facts; it does
    not make an Evidence Role decision and does not mark assertions as accepted.
    """
    assertions: list[EvidenceAssertion] = []

    for segment in document.segments:
        text = segment.text

        # Product and development context
        _first_regex(assertions, document, segment, r"(?:제품명|후보물질명|Product\s*Name|Candidate)\s*[:：]\s*([^\n;|]{2,100})", category="제품", field_path="product.product_name", label_ko="후보물질명")
        _first_regex(assertions, document, segment, r"(?:유효성분|활성성분|Active\s*(?:Substance|Ingredient)|Sequence)\s*[:：]\s*([^\n;|]{2,130})", category="제품", field_path="product.active_substance", label_ko="유효성분/서열")
        _first_regex(assertions, document, segment, r"(?:표적|Target|Mechanism(?:\s*of\s*Action)?|작용기전)\s*[:：]\s*([^\n;|]{2,150})", category="제품", field_path="product.target_mechanism", label_ko="표적·작용기전")
        _first_regex(assertions, document, segment, r"(?:전달체|Carrier|Formulation|제형)\s*[:：]\s*([^\n;|]{2,160})", category="제품", field_path="product.carrier_formulation", label_ko="전달체·제형")

        _keyword_assertion(assertions, document, segment, patterns=[r"\bsiRNA\b.*(?:nano|나노)|(?:nano|나노).*\bsiRNA\b"], category="제품", field_path="product.modality", label_ko="제품 Modality", proposed_value="siRNA + 나노의약품", confidence=0.82)
        _keyword_assertion(assertions, document, segment, patterns=[r"\bsiRNA\b"], category="제품", field_path="product.modality", label_ko="제품 Modality", proposed_value="siRNA 치료제", confidence=0.70)
        _keyword_assertion(assertions, document, segment, patterns=[r"nanoparticle|nanomedicine|나노입자|나노의약품"], category="제품", field_path="product.modality", label_ko="제품 Modality", proposed_value="나노의약품", confidence=0.70)
        _keyword_assertion(assertions, document, segment, patterns=[r"small[- ]?molecule|저분자"], category="제품", field_path="product.modality", label_ko="제품 Modality", proposed_value="저분자 NME", confidence=0.70)
        _keyword_assertion(assertions, document, segment, patterns=[r"intravenous|\bIV\b|정맥(?:투여|주사)?"], category="제품", field_path="product.route", label_ko="투여경로", proposed_value="정맥투여")
        _keyword_assertion(assertions, document, segment, patterns=[r"repeat(?:ed)?\s*(?:dose|exposure)|반복(?:투여|노출)"], category="노출", field_path="product.exposure_pattern", label_ko="노출 형태", proposed_value="반복 노출")
        _keyword_assertion(assertions, document, segment, patterns=[r"single\s*(?:dose|exposure)|단회(?:투여|노출)"], category="노출", field_path="product.exposure_pattern", label_ko="노출 형태", proposed_value="단회 노출")
        _keyword_assertion(assertions, document, segment, patterns=[r"quantitative\s+biodistribution|정량적\s*(?:조직)?분포"], category="노출", field_path="product.distribution_status", label_ko="조직분포", proposed_value="정량적 자료")
        _keyword_assertion(assertions, document, segment, patterns=[r"qualitative\s+biodistribution|정성적\s*(?:조직)?분포"], category="노출", field_path="product.distribution_status", label_ko="조직분포", proposed_value="정성적 자료")

        # AI model card
        _first_regex(assertions, document, segment, r"(?:모델명|Model\s*Name)\s*[:：]\s*([^\n;|]{2,120})", category="AI 모델", field_path="ai_model.model_name", label_ko="AI 모델명")
        _first_regex(assertions, document, segment, r"(?:모델\s*)?(?:버전|Version)\s*[:：]?\s*(v?\d+(?:\.\d+){0,3}[A-Za-z0-9._-]*)", category="AI 모델", field_path="ai_model.model_version", label_ko="AI 모델 버전")
        _first_regex(assertions, document, segment, r"Sensitivity\s*[:=]\s*(\d+(?:\.\d+)?)\s*%?", category="AI 모델", field_path="ai_model.sensitivity_percent", label_ko="Sensitivity", value_type="float")
        _first_regex(assertions, document, segment, r"Specificity\s*[:=]\s*(\d+(?:\.\d+)?)\s*%?", category="AI 모델", field_path="ai_model.specificity_percent", label_ko="Specificity", value_type="float")
        _first_regex(assertions, document, segment, r"(?:False[- ]?negative(?:\s*rate)?|거짓\s*음성률)\s*[:=]\s*(\d+(?:\.\d+)?)\s*%?", category="AI 모델", field_path="ai_model.false_negative_rate_percent", label_ko="False-negative rate", value_type="float")
        _keyword_assertion(assertions, document, segment, patterns=[r"external\s+validation|외부\s*(?:독립\s*)?검증"], category="AI 모델", field_path="ai_model.external_validation", label_ko="외부 독립검증", proposed_value="확인됨", confidence=0.76)
        _keyword_assertion(assertions, document, segment, patterns=[r"calibrat(?:ed|ion).*valid|확률\s*보정.*검증"], category="AI 모델", field_path="ai_model.calibration_status", label_ko="Calibration", proposed_value="검증됨", confidence=0.76)
        _keyword_assertion(assertions, document, segment, patterns=[r"hepatotoxicity|drug[- ]?induced\s+liver\s+injury|\bDILI\b|간독성|약물유발\s*간손상"], category="AI 모델", field_path="ai_model.endpoint", label_ko="AI 예측 Endpoint", proposed_value="초기 간독성", confidence=0.78)
        _keyword_assertion(assertions, document, segment, patterns=[r"(?:prediction|예측|result|결과)[^\n]{0,70}(?:negative|음성|low\s+risk|낮은\s*위험)"], category="AI 모델", field_path="ai_model.result", label_ko="AI 예측 결과", proposed_value="음성 / 낮은 위험 예측", confidence=0.80)
        _keyword_assertion(assertions, document, segment, patterns=[r"(?:prediction|예측|result|결과)[^\n]{0,70}(?:positive|양성|high\s+risk|높은\s*위험)"], category="AI 모델", field_path="ai_model.result", label_ko="AI 예측 결과", proposed_value="양성 / 위험 신호", confidence=0.80)
        _keyword_assertion(assertions, document, segment, patterns=[r"training[^\n]{0,90}small[- ]?molecule|학습[^\n]{0,90}저분자"], category="AI 모델", field_path="ai_model.domain_modalities", label_ko="AI 학습 Modality", proposed_value="저분자", value_type="list", confidence=0.78)
        _keyword_assertion(assertions, document, segment, patterns=[r"training[^\n]{0,90}oligonucleotide|학습[^\n]{0,90}올리고"], category="AI 모델", field_path="ai_model.domain_modalities", label_ko="AI 학습 Modality", proposed_value="올리고뉴클레오타이드", value_type="list", confidence=0.78)
        _keyword_assertion(assertions, document, segment, patterns=[r"training[^\n]{0,90}nano|학습[^\n]{0,90}나노"], category="AI 모델", field_path="ai_model.domain_modalities", label_ko="AI 학습 Modality", proposed_value="나노의약품", value_type="list", confidence=0.78)

        # NAM card
        _keyword_assertion(assertions, document, segment, patterns=[r"2D\s*(?:cell|culture)|2차원\s*세포"], category="NAM 시험", field_path="nam_assay.nam_type", label_ko="NAM 유형", proposed_value="2D 세포시험")
        _keyword_assertion(assertions, document, segment, patterns=[r"co[- ]?culture|공배양"], category="NAM 시험", field_path="nam_assay.nam_type", label_ko="NAM 유형", proposed_value="공배양(Coculture)")
        _keyword_assertion(assertions, document, segment, patterns=[r"spheroid"], category="NAM 시험", field_path="nam_assay.nam_type", label_ko="NAM 유형", proposed_value="3D 간 Spheroid")
        _keyword_assertion(assertions, document, segment, patterns=[r"organoid"], category="NAM 시험", field_path="nam_assay.nam_type", label_ko="NAM 유형", proposed_value="간 Organoid")
        _keyword_assertion(assertions, document, segment, patterns=[r"organ[- ]?on[- ]?chip|liver[- ]?on[- ]?chip|microphysiological|\bMPS\b"], category="NAM 시험", field_path="nam_assay.nam_type", label_ko="NAM 유형", proposed_value="Liver-on-chip / MPS")
        _keyword_assertion(assertions, document, segment, patterns=[r"human[- ]?derived|primary\s+human|사람\s*유래"], category="NAM 시험", field_path="nam_assay.system_origin", label_ko="시험계 기원", proposed_value="사람 유래")
        _keyword_assertion(assertions, document, segment, patterns=[r"hepatocyte|간세포"], category="NAM 시험", field_path="nam_assay.cell_types", label_ko="포함 세포", proposed_value="간세포(Hepatocyte)", value_type="list")
        _keyword_assertion(assertions, document, segment, patterns=[r"Kupffer"], category="NAM 시험", field_path="nam_assay.cell_types", label_ko="포함 세포", proposed_value="Kupffer cell", value_type="list")
        _keyword_assertion(assertions, document, segment, patterns=[r"stellate"], category="NAM 시험", field_path="nam_assay.cell_types", label_ko="포함 세포", proposed_value="Stellate cell", value_type="list")
        _keyword_assertion(assertions, document, segment, patterns=[r"(?:NAM|assay|시험)[^\n]{0,80}(?:negative|음성)"], category="NAM 시험", field_path="nam_assay.result", label_ko="NAM 결과", proposed_value="음성", confidence=0.78)
        _keyword_assertion(assertions, document, segment, patterns=[r"(?:NAM|assay|시험)[^\n]{0,80}(?:positive|양성)"], category="NAM 시험", field_path="nam_assay.result", label_ko="NAM 결과", proposed_value="양성", confidence=0.78)
        _keyword_assertion(assertions, document, segment, patterns=[r"positive\s+control[^\n]{0,80}(?:valid|pass)|양성대조군[^\n]{0,80}(?:유효|통과)"], category="NAM 시험", field_path="nam_assay.positive_control", label_ko="양성대조군", proposed_value="유효")
        _keyword_assertion(assertions, document, segment, patterns=[r"negative\s+control[^\n]{0,80}(?:valid|pass)|음성대조군[^\n]{0,80}(?:유효|통과)"], category="NAM 시험", field_path="nam_assay.negative_control", label_ko="음성대조군", proposed_value="유효")
        _keyword_assertion(assertions, document, segment, patterns=[r"carrier[- ]?only\s+control[^\n]{0,60}(?:included|yes)|전달체\s*단독대조군[^\n]{0,60}(?:포함|있음)"], category="NAM 시험", field_path="nam_assay.carrier_only_control", label_ko="Carrier-only 대조군", proposed_value="포함")
        _keyword_assertion(assertions, document, segment, patterns=[r"free\s+concentration|intracellular\s+concentration|measured\s+exposure|실제\s*(?:세포내|유리)\s*농도"], category="노출", field_path="nam_assay.measured_exposure", label_ko="실제 노출", proposed_value="측정됨")
        _keyword_assertion(assertions, document, segment, patterns=[r"\bQIVIVE\b|\bPBPK\b"], category="노출", field_path="nam_assay.qivive_pbpk", label_ko="QIVIVE/PBPK", proposed_value="수행됨")
        _keyword_assertion(assertions, document, segment, patterns=[r"repeat(?:ed)?\s+exposure|반복\s*노출"], category="NAM 시험", field_path="nam_assay.exposure_design", label_ko="NAM 노출설계", proposed_value="반복노출")
        _keyword_assertion(assertions, document, segment, patterns=[r"single\s+(?:exposure|24[- ]?h)|급성\s*단회|단회\s*노출"], category="NAM 시험", field_path="nam_assay.exposure_design", label_ko="NAM 노출설계", proposed_value="단회/급성 노출")
        _keyword_assertion(assertions, document, segment, patterns=[r"CYP(?:450)?|metabolic\s+competence|대사능"], category="NAM 시험", field_path="nam_assay.metabolic_competence", label_ko="대사능", proposed_value="부분 확인", confidence=0.68)
        _keyword_assertion(assertions, document, segment, patterns=[r"inter[- ]?day|inter[- ]?lot|donor\s+variability|재현성"], category="NAM 시험", field_path="nam_assay.reproducibility", label_ko="재현성", proposed_value="일부 확인", confidence=0.68)
        _keyword_assertion(assertions, document, segment, patterns=[r"cell\s+viability|\bATP\b|세포\s*생존"], category="NAM 시험", field_path="nam_assay.endpoints", label_ko="NAM Endpoint", proposed_value="Cell viability / ATP", value_type="list")
        _keyword_assertion(assertions, document, segment, patterns=[r"mitochondrial|미토콘드리아"], category="NAM 시험", field_path="nam_assay.endpoints", label_ko="NAM Endpoint", proposed_value="미토콘드리아 기능", value_type="list")
        _keyword_assertion(assertions, document, segment, patterns=[r"cytokine|IL-6|TNF[- ]?alpha|사이토카인"], category="NAM 시험", field_path="nam_assay.endpoints", label_ko="NAM Endpoint", proposed_value="Cytokine", value_type="list")

        # Supporting evidence flags
        _keyword_assertion(assertions, document, segment, patterns=[r"mechanis(?:m|tic)|기전(?:적| 기반)?"], category="보조 근거", field_path="supporting_evidence.mechanistic_evidence", label_ko="기전 기반 근거", proposed_value="true", value_type="bool", confidence=0.64)
        _keyword_assertion(assertions, document, segment, patterns=[r"class\s+effect|class\s+toxicity|동일\s*계열|계열\s*독성"], category="보조 근거", field_path="supporting_evidence.class_or_clinical_evidence", label_ko="동일계열/임상 Class 근거", proposed_value="true", value_type="bool", confidence=0.70)
        _keyword_assertion(assertions, document, segment, patterns=[r"quantitative\s+biodistribution|정량적\s*(?:조직)?분포"], category="보조 근거", field_path="supporting_evidence.quantitative_biodistribution", label_ko="정량적 Biodistribution", proposed_value="true", value_type="bool", confidence=0.82)
        _keyword_assertion(assertions, document, segment, patterns=[r"toxicokinetic|\bTK\b|pharmacokinetic|\bPK\b|노출[-– ]?반응"], category="보조 근거", field_path="supporting_evidence.pk_tk_evidence", label_ko="PK/TK 근거", proposed_value="true", value_type="bool", confidence=0.68)
        _keyword_assertion(assertions, document, segment, patterns=[r"in\s+vivo|동물\s*시험|반복투여\s*독성"], category="보조 근거", field_path="supporting_evidence.existing_in_vivo_evidence", label_ko="기존 in vivo 근거", proposed_value="true", value_type="bool", confidence=0.66)
        _keyword_assertion(assertions, document, segment, patterns=[r"clinical\s+(?:evidence|safety)|human\s+(?:data|evidence)|임상\s*안전|사람\s*근거"], category="보조 근거", field_path="supporting_evidence.human_evidence", label_ko="사람/임상 근거", proposed_value="true", value_type="bool", confidence=0.72)

    return assertions


def extract_assertions_from_documents(documents: Iterable[DocumentRecord]) -> list[EvidenceAssertion]:
    assertions: list[EvidenceAssertion] = []
    for document in documents:
        assertions.extend(extract_assertions(document))
    return assertions


def _coerce(value: str, value_type: str) -> Any:
    value = (value or "").strip()
    if value_type == "bool":
        return value.lower() in {"true", "1", "yes", "y", "예", "있음", "확인"}
    if value_type == "float":
        try:
            return float(value.replace("%", "").strip())
        except ValueError:
            return None
    if value_type == "int":
        try:
            return int(float(value))
        except ValueError:
            return None
    if value_type == "list":
        return [item.strip() for item in re.split(r"[,;|]", value) if item.strip()]
    return value


def _set_path(root: Any, path: str, value: Any, value_type: str) -> None:
    parts = path.split(".")
    if len(parts) != 2:
        raise ValueError(f"Unsupported field path: {path}")
    parent_name, attribute = parts
    parent = getattr(root, parent_name)
    if not is_dataclass(parent):
        raise TypeError(f"Target is not a dataclass: {parent_name}")
    field_names = {item.name for item in fields(parent)}
    if attribute not in field_names:
        raise AttributeError(f"Unknown target attribute: {path}")

    coerced = _coerce(str(value), value_type)
    if coerced is None and value_type in {"float", "int"}:
        return
    current = getattr(parent, attribute)
    if value_type == "list":
        merged = list(current or [])
        for item in coerced:
            if item not in merged:
                merged.append(item)
        setattr(parent, attribute, merged)
    else:
        setattr(parent, attribute, coerced)


def apply_reviewed_assertions(inp: AssessmentInput, assertions: Iterable[EvidenceAssertion]) -> AssessmentInput:
    """Apply only human-reviewed assertions to a copy of AssessmentInput."""
    updated = copy.deepcopy(inp)
    reviewed = [item for item in assertions if item.review_status in REVIEWED_STATUSES]
    for assertion in reviewed:
        try:
            _set_path(updated, assertion.field_path, assertion.proposed_value, assertion.value_type)
        except (AttributeError, TypeError, ValueError):
            continue

    if reviewed:
        updated.supporting_evidence.assertions_reviewed = True
        updated.supporting_evidence.evidence_traceable = all(
            item.source_document_name and item.source_location for item in reviewed
        )
    return updated


def assertion_table_rows(assertions: Iterable[EvidenceAssertion]) -> list[dict[str, Any]]:
    return [
        {
            "Assertion ID": item.assertion_id,
            "분류": item.category,
            "평가 필드": item.label_ko,
            "Field Path": item.field_path,
            "제안/수정 값": item.proposed_value,
            "형식": item.value_type,
            "출처 문서": item.source_document_name,
            "출처 위치": item.source_location,
            "근거 발췌": item.source_excerpt,
            "추출 신뢰도": item.confidence,
            "검토 상태": item.review_status,
            "검토 메모": item.reviewer_note,
        }
        for item in assertions
    ]


def assertions_from_table_rows(rows: Iterable[dict[str, Any]], existing: Iterable[EvidenceAssertion]) -> list[EvidenceAssertion]:
    existing_by_id = {item.assertion_id: item for item in existing}
    output: list[EvidenceAssertion] = []
    for row in rows:
        assertion_id = str(row.get("Assertion ID", ""))
        base = existing_by_id.get(assertion_id)
        if not base:
            continue
        base.proposed_value = str(row.get("제안/수정 값", base.proposed_value))
        base.review_status = str(row.get("검토 상태", base.review_status))
        base.reviewer_note = str(row.get("검토 메모", base.reviewer_note))
        output.append(base)
    return output
