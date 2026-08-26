from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
from typing import Iterable

from . import __ontology_version__, __rule_set_version__
from .models import AssessmentInput, AssessmentResult, DataGap, GateResult


ROLE_DEFINITIONS = {
    0: ("R0", "평가 불가", "필수 정보 또는 유효한 근거가 부족하여 현재 사용 가능한 근거 역할을 정할 수 없습니다."),
    1: ("R1", "가설 생성", "잠재 독성위험 또는 기전을 제안하는 수준입니다. 안전성 결론이나 동물시험 축소 근거로 사용할 수 없습니다."),
    2: ("R2", "초기 선별", "후보 우선순위와 추가시험 선택에는 사용할 수 있으나, 동물시험 축소·대체를 지지하지 않습니다."),
    3: ("R3", "보조 근거", "다른 신뢰 가능한 근거와 함께 초기 독성판단을 보조할 수 있습니다."),
    4: ("R4", "동물시험 축소 지원", "정의된 조건 아래 특정 동물 수·용량군·endpoint 범위 축소를 지원할 수 있습니다."),
    5: ("R5", "특정 시험 대체 후보", "좁게 정의된 사용 맥락에서 특정 endpoint 대체를 전문가·규제기관과 논의할 후보입니다."),
}


def _add_gap(
    gaps: list[DataGap],
    code: str,
    title: str,
    description: str,
    criticality: str,
    rule_id: str,
    effect: str,
    recommendation: str,
) -> None:
    if any(g.code == code for g in gaps):
        return
    gaps.append(
        DataGap(
            code=code,
            title=title,
            description=description,
            criticality=criticality,
            rule_id=rule_id,
            effect=effect,
            recommendation=recommendation,
        )
    )


def _bounded(value: float, low: float = 0.0, high: float = 4.0) -> float:
    return round(max(low, min(high, value)), 1)


def _average(values: Iterable[float]) -> float:
    data = list(values)
    return sum(data) / len(data) if data else 0.0


def _modality_covered(inp: AssessmentInput) -> bool:
    modality = inp.product.modality
    domain = set(inp.ai_model.domain_modalities)
    if modality == "저분자 NME":
        return "저분자" in domain
    if modality in {"올리고뉴클레오타이드", "siRNA 치료제"}:
        return "올리고뉴클레오타이드" in domain
    if modality == "나노의약품":
        return "나노의약품" in domain
    if modality == "siRNA + 나노의약품":
        return {"올리고뉴클레오타이드", "나노의약품"}.issubset(domain)
    if modality == "바이오의약품":
        return "바이오의약품" in domain
    return False


def _domain_status(inp: AssessmentInput) -> str:
    if not inp.ai_model.use_ai:
        return "해당 없음"
    if inp.ai_model.domain_status != "자동 평가":
        return inp.ai_model.domain_status
    return "In-domain" if _modality_covered(inp) else "Out-of-domain"


def _model_risk(inp: AssessmentInput) -> str:
    score = inp.context_of_use.model_influence * inp.context_of_use.decision_consequence
    if score >= 20:
        return "매우 높음"
    if score >= 12:
        return "높음"
    if score >= 6:
        return "중간"
    return "낮음"


def _method_credibility(inp: AssessmentInput, gaps: list[DataGap]) -> float:
    scores: list[float] = []
    ai = inp.ai_model
    nam = inp.nam_assay

    if ai.use_ai:
        score = 0.0
        if ai.model_name and ai.model_version:
            score += 0.8
        else:
            _add_gap(
                gaps,
                "ET-G002",
                "AI 모델 식별정보 부족",
                "모델명과 정확한 버전이 모두 필요합니다.",
                "결정 제한",
                "ET-R001",
                "AI 결과의 재현성과 변경이력을 확인할 수 없음",
                "모델명, 버전, 개발자 및 모델카드를 확보하십시오.",
            )
        if ai.endpoint:
            score += 0.35
        if ai.external_validation == "확인됨":
            score += 0.85
        elif ai.external_validation == "부분적으로 확인":
            score += 0.45
        elif ai.external_validation in {"없음", "불명확"}:
            _add_gap(
                gaps,
                "ET-G004",
                "AI 외부검증 부족",
                "독립적인 외부검증 자료 또는 검증집단의 대표성이 충분히 확인되지 않았습니다.",
                "주요 보완",
                "ET-R004",
                "방법 신뢰성 제한",
                "독립 외부검증 자료, 검증집단 특성 및 confidence interval을 확인하십시오.",
            )
        if ai.sensitivity_percent is not None:
            score += 0.45
        if ai.specificity_percent is not None:
            score += 0.4
        if ai.false_negative_rate_percent is not None:
            score += 0.65
        elif ai.result == "음성 / 낮은 위험 예측":
            _add_gap(
                gaps,
                "ET-G005",
                "False-negative 성능 미상",
                "음성예측을 고영향 의사결정에 사용하려면 false-negative 특성이 필요합니다.",
                "결정 제한",
                "ET-R005",
                "음성예측의 근거 역할을 R2 이하로 제한할 수 있음",
                "현재 endpoint와 threshold에서 sensitivity, false-negative rate 및 신뢰구간을 확보하십시오.",
            )
        if ai.calibration_status == "검증됨":
            score += 0.5
        elif ai.calibration_status == "부분 검증":
            score += 0.25
        if ai.source:
            score += 0.35
        scores.append(_bounded(score))

    if nam.use_nam:
        score = 0.0
        if nam.nam_type:
            score += 0.35
        if nam.protocol_completeness == "완결":
            score += 0.85
        elif nam.protocol_completeness == "부분적":
            score += 0.4
        else:
            _add_gap(
                gaps,
                "ET-G010",
                "NAM 프로토콜 불충분",
                "시험법, acceptance criteria 및 실행조건이 충분히 기술되지 않았습니다.",
                "결정 제한",
                "ET-R006",
                "이번 NAM 실행의 유효성 제한",
                "시험 프로토콜, acceptance criteria, 통계 판정법 및 deviation 기록을 완결하십시오.",
            )
        if nam.positive_control == "유효":
            score += 0.7
        else:
            _add_gap(
                gaps,
                "ET-G011",
                "양성대조군 유효성 부족",
                "양성대조군 실패 또는 누락 시 이번 NAM 실행을 유효하다고 볼 수 없습니다.",
                "결정 제한",
                "ET-R006",
                "NAM 결과를 Uninterpretable로 분류",
                "유효한 양성대조군으로 시험 성능을 다시 확인하십시오.",
            )
        if nam.negative_control == "유효":
            score += 0.55
        else:
            _add_gap(
                gaps,
                "ET-G012",
                "음성대조군 유효성 부족",
                "음성대조군 실패 또는 누락으로 배경 반응을 해석하기 어렵습니다.",
                "결정 제한",
                "ET-R006",
                "NAM 결과를 Uninterpretable로 분류",
                "음성대조군과 배경반응 기준을 보완하십시오.",
            )
        if nam.reproducibility == "Donor/lot/반복 재현성 확인":
            score += 0.95
        elif nam.reproducibility == "일부 확인":
            score += 0.45
        else:
            _add_gap(
                gaps,
                "ET-G013",
                "NAM 재현성 자료 부족",
                "Donor, lot 또는 반복실험 간 재현성이 확인되지 않았습니다.",
                "주요 보완",
                "ET-R006",
                "방법 신뢰성 제한",
                "Donor, lot, 실험일 및 가능하면 외부 실험실 간 재현성을 평가하십시오.",
            )
        if nam.endpoints:
            score += min(0.55, len(nam.endpoints) * 0.12)
        if nam.result == "시험 무효":
            score = 0.0
        scores.append(_bounded(score))

    return _bounded(_average(scores))


def _candidate_applicability(inp: AssessmentInput, gaps: list[DataGap]) -> float:
    scores: list[float] = []
    if inp.ai_model.use_ai:
        status = _domain_status(inp)
        score = {
            "In-domain": 4.0,
            "Borderline": 2.4,
            "Out-of-domain": 0.5,
            "Unknown": 1.0,
            "해당 없음": 0.0,
        }.get(status, 1.0)
        if inp.ai_model.endpoint != inp.context_of_use.target_endpoint:
            score = 0.0
            _add_gap(
                gaps,
                "ET-G003",
                "AI Endpoint 불일치",
                "AI가 예측한 endpoint와 현재 독성질문이 일치하지 않습니다.",
                "결정 제한",
                "ET-R002",
                "Fit-for-purpose 부적절; Evidence Role R0",
                "현재 독성질문과 동일한 endpoint를 검증한 방법으로 재평가하십시오.",
            )
        if status == "Out-of-domain":
            _add_gap(
                gaps,
                "ET-G006",
                "AI 적용범위 밖",
                "현재 후보의 modality 또는 특성이 모델 학습·검증범위에 포함되지 않습니다.",
                "결정 제한",
                "ET-R003",
                "음성예측을 Reliable Negative로 인정하지 않으며 최대 R1",
                "현재 modality를 포함하는 모델 또는 독립적인 orthogonal NAM을 사용하십시오.",
            )
        elif status in {"Unknown", "Borderline"}:
            _add_gap(
                gaps,
                "ET-G007",
                "AI 적용범위 불명확",
                "후보가 모델 applicability domain 안에 있는지 충분히 판단할 수 없습니다.",
                "주요 보완",
                "ET-R003",
                "AI 결과 사용범위 제한",
                "구조적 유사성, modality coverage, exposure range 및 nearest-neighbor 근거를 확보하십시오.",
            )
        scores.append(score)

    if inp.nam_assay.use_nam:
        score = 2.5
        if inp.context_of_use.target_endpoint != "초기 간독성":
            score = 1.3
        if inp.nam_assay.system_origin == "사람 유래":
            score += 0.5
        if "나노의약품" in inp.product.modality and inp.nam_assay.measured_exposure == "측정 안 됨":
            score -= 0.7
        scores.append(_bounded(score))

    return _bounded(_average(scores))


def _human_relevance(inp: AssessmentInput, gaps: list[DataGap]) -> float:
    nam = inp.nam_assay
    supporting = inp.supporting_evidence
    if not nam.use_nam:
        score = 0.0
        if supporting.human_evidence:
            score += 1.2
        if supporting.mechanistic_evidence:
            score += 0.6
        if score < 2.0:
            _add_gap(
                gaps,
                "ET-G014",
                "사람 관련 NAM 근거 부족",
                "AI 예측만으로 사람 생물학적 관련성을 충분히 확립할 수 없습니다.",
                "주요 보완",
                "ET-R010",
                "사람 관련성 및 Evidence Role 제한",
                "사람 유래 간 모델, 임상 class 또는 사람 조직 기반 기전근거를 추가하십시오.",
            )
        return _bounded(score)

    score = 0.0
    if nam.system_origin == "사람 유래":
        score += 1.0
    elif nam.system_origin == "사람·동물 혼합":
        score += 0.5

    if "간세포(Hepatocyte)" in nam.cell_types:
        score += 0.8
    else:
        _add_gap(
            gaps,
            "ET-G015",
            "간세포 구성 누락",
            "간독성 Context of Use에서 관련 hepatocyte 기능이 필요합니다.",
            "결정 제한",
            "ET-R010",
            "사람 관련성 낮음",
            "기능이 확인된 사람 간세포를 포함하십시오.",
        )

    if "Kupffer cell" in nam.cell_types or nam.immune_competence == "충분":
        score += 0.7
    elif inp.product.modality in {"나노의약품", "siRNA + 나노의약품", "siRNA 치료제", "올리고뉴클레오타이드"}:
        _add_gap(
            gaps,
            "ET-G016",
            "면역·Kupffer cell 반응 미평가",
            "나노입자 또는 올리고뉴클레오타이드에서는 간 면역반응의 불확실성이 큽니다.",
            "주요 보완",
            "ET-R010",
            "사람 관련성 및 면역기전 해석 제한",
            "Kupffer cell 공배양, cytokine 또는 보완적인 면역 적격 간 모델을 추가하십시오.",
        )

    if any(cell in nam.cell_types for cell in {"Stellate cell", "간 내피세포", "담관세포"}):
        score += 0.4

    if nam.metabolic_competence == "충분히 확인":
        score += 0.8
    elif nam.metabolic_competence == "부분 확인":
        score += 0.4
    else:
        _add_gap(
            gaps,
            "ET-G017",
            "대사능 미확인",
            "CYP 및 간 대사기능이 확인되지 않아 사람 간독성 번역성이 제한됩니다.",
            "주요 보완",
            "ET-R010",
            "대사체 매개 독성 평가 제한",
            "CYP와 핵심 간기능이 확인된 시험계로 대사 관련성을 보강하십시오.",
        )

    if supporting.human_evidence:
        score += 0.4
    if supporting.mechanistic_evidence:
        score += 0.3
    return _bounded(score)


def _exposure_relevance(inp: AssessmentInput, gaps: list[DataGap]) -> float:
    product = inp.product
    nam = inp.nam_assay
    score = 0.0

    if product.human_cmax or product.human_auc:
        score += 1.0
    else:
        _add_gap(
            gaps,
            "ET-G018",
            "사람 예상노출 정보 부족",
            "Cmax 또는 AUC가 없어 시험노출과 사람노출을 직접 비교할 수 없습니다.",
            "주요 보완",
            "ET-R007",
            "노출 관련성 제한",
            "예상 사람 Cmax/AUC 또는 초기 PK 가정을 정의하십시오.",
        )

    if nam.use_nam:
        if nam.measured_exposure == "측정됨":
            score += 1.2
        elif nam.measured_exposure == "부분 측정":
            score += 0.55
        else:
            _add_gap(
                gaps,
                "ET-G019",
                "실제 Free/세포내 노출 미측정",
                "명목 농도만으로는 세포 또는 표적조직의 실제 노출을 확인할 수 없습니다.",
                "결정 제한",
                "ET-R008",
                "음성 NAM 결과를 Reliable Negative로 인정하지 않음",
                "명목 농도와 별도로 free 또는 세포내 실제 노출을 측정하십시오.",
            )

        if nam.qivive_pbpk == "수행됨":
            score += 1.0
        elif nam.qivive_pbpk == "초기 연결":
            score += 0.4
        else:
            _add_gap(
                gaps,
                "ET-G020",
                "QIVIVE/PBPK 연결 없음",
                "NAM 결과가 계획된 사람노출로 정량 번역되지 않았습니다.",
                "주요 보완",
                "ET-R007",
                "사람노출 번역 제한",
                "QIVIVE 또는 PBPK를 이용하여 NAM 농도를 사람노출로 연결하십시오.",
            )

        repeat_plan = product.exposure_pattern in {"반복 노출", "지속 노출"}
        repeat_nam = nam.exposure_design in {"반복노출", "지속노출"}
        if (repeat_plan and repeat_nam) or (not repeat_plan and nam.exposure_design == "단회/급성 노출"):
            score += 0.8
        else:
            _add_gap(
                gaps,
                "ET-G021",
                "단회·반복노출 불일치",
                "계획된 반복 또는 지속 노출을 급성 단회시험만으로 지원하고 있습니다.",
                "결정 제한",
                "ET-R009",
                "노출 관련성 및 Evidence Role을 R2 이하로 제한할 수 있음",
                "반복노출 NAM 또는 과학적으로 타당한 acute-to-repeat bridge를 확보하십시오.",
            )

    if product.distribution_status == "정량적 자료":
        score += 0.7
    elif product.distribution_status == "정성적 자료":
        score += 0.25
    else:
        _add_gap(
            gaps,
            "ET-G022",
            "조직분포 자료 부족",
            "표적장기 노출 및 축적 가능성을 확인할 수 없습니다.",
            "주요 보완",
            "ET-R007",
            "조직 노출 번역 제한",
            "정량적 간·비장 biodistribution과 시간경과별 잔류를 확보하십시오.",
        )

    return _bounded(score)


def _evidence_concordance(inp: AssessmentInput, gaps: list[DataGap]) -> tuple[float, int, bool]:
    streams = 0
    score = 0.0
    conflict = False
    ai_result = inp.ai_model.result if inp.ai_model.use_ai else None
    nam_result = inp.nam_assay.result if inp.nam_assay.use_nam and inp.nam_assay.result != "시험 무효" else None

    if inp.ai_model.use_ai:
        streams += 1
    if nam_result:
        streams += 1

    support = inp.supporting_evidence
    for enabled in (
        support.mechanistic_evidence,
        support.class_or_clinical_evidence,
        support.quantitative_biodistribution,
        support.pk_tk_evidence,
        support.existing_in_vivo_evidence,
        support.human_evidence,
    ):
        if enabled:
            streams += 1
            score += 0.35

    if ai_result and nam_result:
        ai_direction = "negative" if ai_result.startswith("음성") else "positive" if ai_result.startswith("양성") else "equivocal"
        nam_direction = "negative" if nam_result == "음성" else "positive" if nam_result == "양성" else "equivocal"
        if ai_direction == nam_direction and ai_direction in {"negative", "positive"}:
            score += 2.0
        elif "equivocal" in {ai_direction, nam_direction}:
            score += 0.8
        else:
            conflict = True
            score += 0.2
            _add_gap(
                gaps,
                "ET-G023",
                "근거 간 상충",
                "AI와 사람 관련 NAM 결과가 반대 방향을 나타냅니다. 원인 규명 전 동물시험 축소를 지지할 수 없습니다.",
                "결정 제한",
                "ET-R011",
                "Evidence Role 최대 R2 및 전문가 검토 필요",
                "상충 원인을 확인할 orthogonal assay와 독립적 전문가 검토를 수행하십시오.",
            )
    elif streams == 1:
        score += 1.2
    elif streams >= 2:
        score += 1.7

    if streams < 2:
        _add_gap(
            gaps,
            "ET-G024",
            "독립적 근거 흐름 부족",
            "하나의 결과만으로 Weight of Evidence를 구성할 수 없습니다.",
            "주요 보완",
            "ET-R012",
            "R4/R5 판정 불가",
            "서로 독립적인 두 번째 근거 흐름을 추가하십시오.",
        )

    return _bounded(score), streams, conflict


def _animal_use_text(role: int) -> tuple[str, str]:
    return {
        0: ("평가 불가", "필수정보 또는 유효한 실행이 부족합니다."),
        1: ("축소·대체 근거 불충분", "추가 근거 확보 전 기존 독성평가를 축소해서는 안 됩니다."),
        2: ("선별 용도로만 사용", "후보 우선순위와 추가시험 선택에는 사용할 수 있으나 동물시험 축소는 지지하지 않습니다."),
        3: ("보조·정교화 가능", "동물시험 설계 정교화에는 활용할 수 있으나 축소에는 추가 검증이 필요합니다."),
        4: ("제한적 축소 지원", "명시된 조건과 endpoint에서 동물 수·용량군·중복시험 축소를 검토할 수 있습니다."),
        5: ("특정 시험 대체 후보", "좁게 정의된 Context of Use에서 전문가 및 규제기관 논의를 위한 대체 후보입니다."),
    }[role]


def evaluate(inp: AssessmentInput) -> AssessmentResult:
    gaps: list[DataGap] = []
    gates: list[GateResult] = []
    cou = inp.context_of_use
    product = inp.product
    ai = inp.ai_model
    nam = inp.nam_assay
    support = inp.supporting_evidence

    if not cou.question_of_interest.strip():
        _add_gap(
            gaps,
            "ET-G001",
            "독성 질문 미정의",
            "Question of Interest가 명확히 정의되지 않았습니다.",
            "결정 제한",
            "ET-R001",
            "Evidence Role R0",
            "독성질문과 Context of Use를 한 문장으로 명확히 정의하십시오.",
        )
    if not product.product_name.strip():
        _add_gap(
            gaps,
            "ET-G001B",
            "후보물질 미정의",
            "평가 대상 후보물질을 확인할 수 없습니다.",
            "결정 제한",
            "ET-R001",
            "Evidence Role R0",
            "후보물질명과 modality를 정의하십시오.",
        )
    if cou.target_endpoint != "초기 간독성":
        _add_gap(
            gaps,
            "ET-G000",
            "MVP 활성범위 밖",
            "현재 v0.4의 상세 규칙은 초기 간독성에 한정됩니다.",
            "결정 제한",
            "ET-R001",
            "Evidence Role R0",
            "초기 간독성 vertical slice로 평가하거나 향후 endpoint 모듈을 추가하십시오.",
        )
    if not ai.use_ai and not nam.use_nam:
        _add_gap(
            gaps,
            "ET-G000B",
            "평가방법 없음",
            "AI 또는 NAM 근거 중 하나 이상을 입력해야 합니다.",
            "결정 제한",
            "ET-R001",
            "Evidence Role R0",
            "적어도 하나의 AI 또는 NAM 결과를 입력하십시오.",
        )
    if product.modality in {"나노의약품", "siRNA + 나노의약품"} and nam.use_nam and nam.carrier_only_control == "미포함":
        _add_gap(
            gaps,
            "ET-G025",
            "Carrier-only 대조군 누락",
            "전달체 자체의 독성기여를 분리할 수 없습니다.",
            "결정 제한",
            "ET-R010",
            "제형 기여도 판단 불가",
            "Carrier-only와 active-only 대조군으로 독성기여를 분리하십시오.",
        )
    if not support.evidence_traceable:
        _add_gap(
            gaps,
            "ET-G026",
            "근거 추적성 부족",
            "결론을 문서·페이지·표·원자료로 추적할 수 없습니다.",
            "결정 제한",
            "ET-R014",
            "Evidence Role 최대 R2",
            "모든 assertion을 문서·페이지·표·원자료와 연결하십시오.",
        )
    if not support.assertions_reviewed:
        _add_gap(
            gaps,
            "ET-G028",
            "구조화 근거 미검토",
            "AI가 추출한 Evidence Assertion을 전문가가 아직 승인하지 않았습니다.",
            "주요 보완",
            "ET-R014",
            "고영향 결론 보류",
            "AI 추출 assertion을 독성전문가가 승인·수정·거절하도록 하십시오.",
        )
    if not support.version_locked:
        _add_gap(
            gaps,
            "ET-G027",
            "버전 기록 부족",
            "모델·시험법·규칙 버전이 고정되지 않았습니다.",
            "주요 보완",
            "ET-R015",
            "재현성과 재평가 범위 불명",
            "모델, NAM, ontology 및 rule set 버전을 기록하십시오.",
        )

    method = _method_credibility(inp, gaps)
    applicability = _candidate_applicability(inp, gaps)
    human = _human_relevance(inp, gaps)
    exposure = _exposure_relevance(inp, gaps)
    concordance, streams, conflict = _evidence_concordance(inp, gaps)

    critical = [g for g in gaps if g.criticality == "결정 제한"]
    role = 0
    if cou.question_of_interest.strip() and product.product_name.strip() and (ai.use_ai or nam.use_nam):
        role = 1
    if method >= 2.0 and applicability >= 2.0:
        role = 2
    if method >= 2.5 and applicability >= 2.5 and human >= 2.0 and exposure >= 2.0 and concordance >= 2.0 and not conflict:
        role = 3
    if (
        method >= 3.0
        and applicability >= 3.0
        and human >= 3.0
        and exposure >= 3.0
        and concordance >= 3.0
        and not critical
        and support.expert_reviewed
        and streams >= 2
    ):
        role = 4
    if (
        role >= 4
        and cou.objective == "특정 독성시험 대체 후보 평가"
        and method >= 3.5
        and applicability >= 3.5
        and human >= 3.5
        and exposure >= 3.5
        and concordance >= 3.5
        and ai.external_validation == "확인됨"
        and ai.false_negative_rate_percent is not None
        and support.evidence_traceable
        and support.assertions_reviewed
        and support.expert_reviewed
        and support.version_locked
    ):
        role = 5

    # Hard caps
    domain = _domain_status(inp)
    if ai.use_ai and ai.result == "음성 / 낮은 위험 예측" and domain == "Out-of-domain":
        role = min(role, 1)
    if (
        ai.use_ai
        and ai.result == "음성 / 낮은 위험 예측"
        and ai.false_negative_rate_percent is None
        and cou.decision_consequence >= 3
    ):
        role = min(role, 2)
    if nam.use_nam and (nam.positive_control != "유효" or nam.negative_control != "유효" or nam.result == "시험 무효"):
        if not ai.use_ai:
            role = min(role, 1)
    if nam.use_nam and nam.result == "음성" and nam.measured_exposure == "측정 안 됨":
        role = min(role, 2)
    if (
        nam.use_nam
        and product.exposure_pattern in {"반복 노출", "지속 노출"}
        and nam.exposure_design == "단회/급성 노출"
    ):
        role = min(role, 2)
    if conflict:
        role = min(role, 2)
    if not support.evidence_traceable:
        role = min(role, 2)
    if not support.expert_reviewed:
        role = min(role, 3)
    if streams < 2:
        role = min(role, 3)
    if not cou.question_of_interest.strip() or not product.product_name.strip() or cou.target_endpoint != "초기 간독성":
        role = 0

    uncertainty = "낮음"
    if len(critical) >= 3:
        uncertainty = "매우 높음"
    elif critical or len(gaps) >= 5:
        uncertainty = "높음"
    elif len(gaps) >= 2:
        uncertainty = "중간"

    gates.extend(
        [
            GateResult("독성 질문·COU", "통과" if cou.question_of_interest and product.product_name else "미통과", "질문과 제품이 정의되어야 합니다.", "미통과 시 R0"),
            GateResult("방법 식별·버전", "통과" if (not ai.use_ai or (ai.model_name and ai.model_version)) else "미통과", "정확한 모델/시험법 버전이 필요합니다.", "미통과 시 R0 또는 R1"),
            GateResult("Endpoint 일치", "통과" if (not ai.use_ai or ai.endpoint == cou.target_endpoint) and cou.target_endpoint == "초기 간독성" else "미통과", "방법 endpoint와 독성질문이 일치해야 합니다.", "미통과 시 R0"),
            GateResult("후보 적용범위", "통과" if not ai.use_ai or domain in {"In-domain", "Borderline"} else "미통과", f"AI domain status: {domain}", "Out-of-domain 음성은 최대 R1"),
            GateResult("NAM 실행 유효성", "통과" if not nam.use_nam or (nam.positive_control == "유효" and nam.negative_control == "유효" and nam.result != "시험 무효") else "미통과", "대조군과 실행상태가 유효해야 합니다.", "무효 실행은 근거 제외"),
            GateResult("사람 관련성", "통과" if human >= 2.5 else "조건부", "관련 세포·대사·면역기능을 확인합니다.", "낮으면 R3 이상 제한"),
            GateResult("노출 번역", "통과" if exposure >= 2.5 else "조건부", "실제 노출 및 사람노출 연결이 필요합니다.", "낮으면 R3 이상 제한"),
            GateResult("독립 근거", "통과" if streams >= 2 else "미통과", f"독립 근거 흐름 {streams}개", "R4/R5에 최소 2개 필요"),
            GateResult("근거 추적성", "통과" if support.evidence_traceable else "미통과", "문서·페이지·표·원자료로 추적되어야 합니다.", "미통과 시 최대 R2"),
            GateResult("전문가 검토", "통과" if support.expert_reviewed else "미통과", "R4/R5에는 독성전문가 승인이 필수입니다.", "미검토 시 최대 R3"),
        ]
    )

    role_code, role_name, role_desc = ROLE_DEFINITIONS[role]
    animal_status, animal_desc = _animal_use_text(role)

    observations: list[str] = [
        f"평가 대상은 {product.product_name or '미정 후보물질'}이며 제품 modality는 {product.modality}, 투여경로는 {product.route}입니다.",
    ]
    if ai.use_ai:
        observations.append(f"AI 모델 {ai.model_name or '(모델명 미상)'} {ai.model_version or '(버전 미상)'}은 {ai.result} 결과를 제시했습니다.")
    if nam.use_nam:
        observations.append(f"{nam.nam_type} NAM에서 {nam.result} 결과가 입력되었고 노출설계는 {nam.exposure_design}입니다.")

    interpretations: list[str] = []
    if ai.use_ai and domain == "Out-of-domain":
        interpretations.append("AI 모델의 일반적 성능과 별개로 현재 후보는 적용범위 밖이므로 음성예측을 낮은 독성우려로 해석할 수 없습니다.")
    if nam.use_nam and nam.result == "음성" and nam.measured_exposure == "측정 안 됨":
        interpretations.append("실제 free 또는 세포내 노출이 입증되지 않아 NAM 음성결과는 Reliable Negative가 아닙니다.")
    if nam.use_nam and product.exposure_pattern in {"반복 노출", "지속 노출"} and nam.exposure_design == "단회/급성 노출":
        interpretations.append("반복 또는 지속 투여계획을 급성 단회 NAM으로만 평가하여 누적·적응·지연독성의 불확실성이 남습니다.")
    if conflict:
        interpretations.append("AI와 NAM 근거가 상충하므로 어느 결과도 우선하지 않고 원인 규명과 독립적 확인이 필요합니다.")
    if not interpretations:
        interpretations.append("현재 방법의 신뢰성·적용성·사람 관련성·노출 관련성을 종합하면 다른 독립적 근거와 함께 제한된 범위에서 활용할 수 있습니다.")

    development_relevance = [
        f"현재 패키지의 Evidence Role은 {role_code} — {role_name}입니다.",
        animal_desc,
        f"잔여 불확실성은 {uncertainty}이며, 모델 위험은 {_model_risk(inp)}입니다.",
    ]
    recommendations = list(dict.fromkeys(g.recommendation for g in gaps))
    if not recommendations:
        recommendations.append("현재 근거 역할의 사용조건을 명확히 문서화하고, 실제 동물시험 변경 전 전문가 및 필요 시 규제기관과 검토하십시오.")

    input_payload = inp.to_dict()
    input_hash = sha256(repr(input_payload).encode("utf-8")).hexdigest()[:16]
    audit = {
        "assessment_id": f"NORA-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "assessment_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "ontology_version": __ontology_version__,
        "rule_set_version": __rule_set_version__,
        "input_hash": input_hash,
        "ai_domain_status": domain,
        "assertions_reviewed": support.assertions_reviewed,
        "expert_reviewed": support.expert_reviewed,
        "evidence_traceable": support.evidence_traceable,
        "version_locked": support.version_locked,
        "expert_review_note": support.expert_review_note,
        "prototype_boundary": "초기 간독성 vertical slice; 연구 및 의사결정 지원용",
    }

    return AssessmentResult(
        evidence_role=role,
        evidence_role_code=role_code,
        evidence_role_name=role_name,
        evidence_role_description=role_desc,
        animal_use_status=animal_status,
        animal_use_description=animal_desc,
        model_risk=_model_risk(inp),
        residual_uncertainty=uncertainty,
        evidence_stream_count=streams,
        scores={
            "방법 신뢰성": method,
            "후보 적용성": applicability,
            "사람 생물학적 관련성": human,
            "노출 관련성": exposure,
            "근거 일치성": concordance,
            "잔여 불확실성": uncertainty,
        },
        gates=gates,
        data_gaps=gaps,
        observations=observations,
        interpretations=interpretations,
        development_relevance=development_relevance,
        recommendations=recommendations,
        audit=audit,
    )
