from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import AIModelCard, AssessmentInput, DataGap, GateResult


@dataclass(frozen=True)
class AICredibilityResult:
    data_credibility: float
    ground_truth_adequacy: float
    performance_adequacy: float
    calibration_adequacy: float | str
    prediction_reliability_score: float
    prediction_reliability_label: str
    lifecycle_governance: float
    gaps: tuple[DataGap, ...]
    gates: tuple[GateResult, ...]

    def profile(self) -> dict[str, float | str]:
        return {
            "데이터 신뢰성": self.data_credibility,
            "Endpoint·Ground Truth 적절성": self.ground_truth_adequacy,
            "예측성능 적절성": self.performance_adequacy,
            "Calibration 적절성": self.calibration_adequacy,
            "개별 예측 신뢰성": self.prediction_reliability_score,
            "Lifecycle·Governance": self.lifecycle_governance,
        }


def _bounded(value: float) -> float:
    return round(max(0.0, min(4.0, value)), 1)


def _average(values: Iterable[float]) -> float:
    data = list(values)
    return sum(data) / len(data) if data else 0.0


def _gap(
    code: str,
    title: str,
    description: str,
    criticality: str,
    rule_id: str,
    effect: str,
    recommendation: str,
) -> DataGap:
    return DataGap(code, title, description, criticality, rule_id, effect, recommendation)


def _data_credibility(ai: AIModelCard, gaps: list[DataGap]) -> float:
    score = 0.0
    if ai.dataset_source and ai.dataset_version:
        score += 0.75
    else:
        gaps.append(
            _gap(
                "AI-G001",
                "학습데이터 출처·버전 불충분",
                "학습·검증 데이터의 출처와 정확한 버전이 모두 확인되지 않았습니다.",
                "주요 보완",
                "AI-R001",
                "데이터 계보와 결과 재현성 제한",
                "데이터 출처, 버전, 생성시점 및 immutable hash를 기록하십시오.",
            )
        )
    if ai.training_sample_size is not None and ai.training_sample_size > 0:
        score += 0.35
    else:
        gaps.append(
            _gap(
                "AI-G002",
                "학습표본 규모 미확인",
                "모델 개발에 사용된 표본 수를 확인할 수 없습니다.",
                "주요 보완",
                "AI-R001",
                "성능추정의 정밀도와 대표성 판단 제한",
                "전체 표본 수와 endpoint별 양성·음성 분포를 제시하십시오.",
            )
        )
    if ai.positive_class_percent is not None:
        score += 0.35
    else:
        gaps.append(
            _gap(
                "AI-G003",
                "Class balance 미확인",
                "독성 양성 비율과 class imbalance가 보고되지 않았습니다.",
                "주요 보완",
                "AI-R002",
                "Accuracy와 AUROC의 해석 제한",
                "양성·음성 비율, prevalence 및 imbalance 처리방법을 보고하십시오.",
            )
        )

    split_scores = {
        "외부 독립검증": 0.6,
        "시간 분할": 0.55,
        "Scaffold 분할": 0.55,
        "무작위 분할": 0.25,
        "불명확": 0.0,
    }
    score += split_scores.get(ai.split_strategy, 0.0)
    if ai.split_strategy == "불명확":
        gaps.append(
            _gap(
                "AI-G004",
                "데이터 분할전략 불명확",
                "Random, scaffold, temporal 또는 external split 중 어떤 검증전략을 사용했는지 확인할 수 없습니다.",
                "주요 보완",
                "AI-R003",
                "일반화 성능 해석 제한",
                "학습·튜닝·시험 세트의 분할단위와 분할시점을 문서화하십시오.",
            )
        )

    independence_scores = {
        "독립 확인": 0.9,
        "부분 확인": 0.4,
        "비독립 / 중복 확인": 0.0,
        "불명확": 0.0,
    }
    score += independence_scores.get(ai.test_set_independence, 0.0)
    if ai.test_set_independence == "비독립 / 중복 확인":
        gaps.append(
            _gap(
                "AI-G005",
                "시험세트 비독립 또는 중복",
                "학습자료와 시험·외부검증 자료가 독립적이지 않거나 동일·유사 항목의 중복이 확인되었습니다.",
                "결정 제한",
                "AI-R003",
                "보고된 검증성능을 독립 예측성으로 인정할 수 없음",
                "중복을 제거하고 독립된 scaffold, temporal 또는 external test set에서 재검증하십시오.",
            )
        )
    elif ai.test_set_independence in {"부분 확인", "불명확"}:
        gaps.append(
            _gap(
                "AI-G006",
                "시험세트 독립성 불충분",
                "학습·튜닝·시험 자료의 독립성과 유사체 중복 여부가 충분히 확인되지 않았습니다.",
                "주요 보완",
                "AI-R003",
                "외부검증 신뢰성 제한",
                "화합물, 염, 이성질체, scaffold 및 출처 단위의 중복검사를 수행하십시오.",
            )
        )

    leakage_scores = {
        "평가 완료 — 문제 없음": 0.85,
        "일부 확인": 0.35,
        "누수 가능성": 0.1,
        "누수 확인": 0.0,
        "미평가": 0.0,
    }
    score += leakage_scores.get(ai.leakage_assessment, 0.0)
    if ai.leakage_assessment == "누수 확인":
        gaps.append(
            _gap(
                "AI-G007",
                "Data leakage 확인",
                "결과정보 또는 시험자료가 학습과 평가 과정 사이에 누출된 정황이 확인되었습니다.",
                "결정 제한",
                "AI-R004",
                "성능평가 무효; Evidence Role 최대 R1",
                "전처리·feature selection을 포함한 전체 pipeline을 독립분할 후 다시 검증하십시오.",
            )
        )
    elif ai.leakage_assessment in {"미평가", "일부 확인", "누수 가능성"}:
        criticality = "결정 제한" if ai.leakage_assessment == "누수 가능성" else "주요 보완"
        gaps.append(
            _gap(
                "AI-G008",
                "Data leakage 평가 불충분",
                "전처리, feature selection, 유사체 중복 및 target-derived feature를 포함한 누수평가가 충분하지 않습니다.",
                criticality,
                "AI-R004",
                "모델 성능 과대평가 가능성",
                "독립 pipeline 기준으로 데이터 누수검사를 수행하고 결과를 보고하십시오.",
            )
        )

    duplicate_scores = {
        "평가 완료 — 문제 없음": 0.5,
        "중복 제거 / 관리": 0.5,
        "일부 확인": 0.2,
        "중복 확인": 0.0,
        "미평가": 0.0,
    }
    score += duplicate_scores.get(ai.duplicate_assessment, 0.0)
    if ai.duplicate_assessment in {"미평가", "중복 확인"}:
        gaps.append(
            _gap(
                "AI-G009",
                "중복·유사체 평가 불충분",
                "동일 화합물, 염, 이성질체 또는 근접 scaffold의 세트 간 중복을 배제하지 못했습니다.",
                "주요 보완",
                "AI-R003",
                "검증성능의 독립성 제한",
                "구조 정규화 후 exact duplicate와 scaffold-level overlap을 평가하십시오.",
            )
        )
    return _bounded(score)


def _ground_truth_adequacy(ai: AIModelCard, gaps: list[DataGap]) -> float:
    score = 0.0
    if ai.endpoint_definition.strip():
        score += 0.8
    else:
        gaps.append(
            _gap(
                "AI-G010",
                "Endpoint 정의 누락",
                "모델의 양성·음성 label이 어떤 임상·병리·시험 기준을 의미하는지 정의되지 않았습니다.",
                "결정 제한",
                "AI-R005",
                "Question of Interest와 모델 output의 의미정합성 판단 불가",
                "endpoint 정의, 관찰기간, severity threshold 및 positive/negative 기준을 명시하십시오.",
            )
        )

    reference_scores = {
        "전문가 adjudication / 임상 기준": 1.2,
        "검증된 in vivo / 병리 기준": 1.0,
        "검증된 NAM 기준": 0.8,
        "문헌 / 라벨 기반": 0.4,
        "불명확": 0.0,
    }
    score += reference_scores.get(ai.reference_standard, 0.0)
    if ai.reference_standard == "불명확":
        gaps.append(
            _gap(
                "AI-G011",
                "Ground truth 불명확",
                "모델 학습 label의 reference standard를 확인할 수 없습니다.",
                "결정 제한",
                "AI-R005",
                "모델 성능과 독성 endpoint의 임상적 의미 제한",
                "임상 adjudication, 병리, validated assay 또는 명시된 reference method를 연결하십시오.",
            )
        )

    quality_scores = {
        "전문가 검토·합의": 1.0,
        "독립적 검토": 0.8,
        "단일 출처 / 자동 라벨": 0.3,
        "불명확": 0.0,
    }
    score += quality_scores.get(ai.label_quality, 0.0)
    if ai.label_quality in {"단일 출처 / 자동 라벨", "불명확"}:
        gaps.append(
            _gap(
                "AI-G012",
                "Label 품질 제한",
                "독성 label이 전문가 합의 또는 독립검토를 거쳤다는 근거가 부족합니다.",
                "주요 보완",
                "AI-R005",
                "Ground-truth 오류가 모델성능에 전파될 수 있음",
                "Blinded expert review, adjudication 또는 label uncertainty 분석을 수행하십시오.",
            )
        )

    missing_policy_scores = {
        "미평가와 음성을 명확히 구분": 0.7,
        "일부 구분": 0.35,
        "미평가를 음성으로 처리": 0.0,
        "불명확": 0.0,
    }
    score += missing_policy_scores.get(ai.missing_label_policy, 0.0)
    if ai.missing_label_policy == "미평가를 음성으로 처리":
        gaps.append(
            _gap(
                "AI-G013",
                "미평가 자료를 음성으로 라벨링",
                "Not tested 또는 not reported가 negative toxicity label로 처리되었습니다.",
                "결정 제한",
                "AI-R006",
                "음성 class 오염 및 false reassurance 위험",
                "미평가·결측·비보고 상태를 음성 label과 분리하여 재구축하십시오.",
            )
        )
    elif ai.missing_label_policy in {"일부 구분", "불명확"}:
        gaps.append(
            _gap(
                "AI-G014",
                "Missing-label 정책 불충분",
                "미평가, 결측, 비보고와 실제 음성을 어떻게 구분했는지 충분히 확인되지 않았습니다.",
                "주요 보완",
                "AI-R006",
                "음성 label 신뢰성 제한",
                "Missingness taxonomy와 label assignment rule을 문서화하십시오.",
            )
        )

    if ai.time_window_defined:
        score += 0.35
    else:
        gaps.append(
            _gap(
                "AI-G015",
                "독성 관찰기간 미정의",
                "급성, 반복, 지연성 또는 누적 독성 중 어떤 시간범위를 예측하는지 불명확합니다.",
                "주요 보완",
                "AI-R005",
                "현재 투여기간과의 정합성 판단 제한",
                "학습 endpoint의 관찰기간과 현재 Context of Use의 투여기간을 명시하십시오.",
            )
        )
    if ai.severity_threshold_defined:
        score += 0.35
    else:
        gaps.append(
            _gap(
                "AI-G016",
                "중증도 기준 미정의",
                "경미한 변화와 adverse 또는 임상적으로 중대한 독성을 구분하는 기준이 없습니다.",
                "주요 보완",
                "AI-R005",
                "양성예측의 개발상 의미 불명확",
                "severity/adversity threshold와 판정자를 명시하십시오.",
            )
        )
    return _bounded(score)


def _performance_adequacy(ai: AIModelCard, gaps: list[DataGap]) -> float:
    score = 0.0
    metrics = [
        ai.sensitivity_percent,
        ai.specificity_percent,
        ai.false_negative_rate_percent,
        ai.false_positive_rate_percent,
        ai.ppv_percent,
        ai.npv_percent,
        ai.balanced_accuracy_percent,
        ai.auroc,
        ai.auprc,
    ]
    provided = sum(value is not None for value in metrics)
    score += min(1.6, provided * 0.22)

    if ai.sensitivity_percent is None or ai.specificity_percent is None:
        gaps.append(
            _gap(
                "AI-G017",
                "핵심 분류성능 미보고",
                "Sensitivity와 specificity 중 하나 이상이 보고되지 않았습니다.",
                "결정 제한",
                "AI-R007",
                "Accuracy만으로 독성모델 성능을 판단할 수 없음",
                "Sensitivity, specificity 및 threshold별 confusion matrix를 보고하십시오.",
            )
        )
    if ai.result == "음성 / 낮은 위험 예측" and (
        ai.false_negative_rate_percent is None or ai.npv_percent is None
    ):
        gaps.append(
            _gap(
                "AI-G018",
                "음성예측 성능 불충분",
                "현재 음성예측을 해석하는 데 필요한 false-negative rate 또는 NPV가 부족합니다.",
                "결정 제한",
                "AI-R007",
                "Prediction Reliability 최대 중간",
                "해당 endpoint, prevalence 및 threshold에서 FNR과 NPV를 보고하십시오.",
            )
        )
    if ai.result == "양성 / 위험 신호" and ai.ppv_percent is None:
        gaps.append(
            _gap(
                "AI-G019",
                "양성예측의 PPV 미보고",
                "양성예측 중 실제 양성 비율을 확인할 수 없습니다.",
                "주요 보완",
                "AI-R007",
                "양성신호의 확인시험 우선순위 판단 제한",
                "현재 prevalence와 threshold에 대한 PPV 및 confidence interval을 보고하십시오.",
            )
        )

    if ai.performance_confidence_intervals == "보고됨":
        score += 0.65
    elif ai.performance_confidence_intervals == "부분 보고":
        score += 0.3
        gaps.append(
            _gap(
                "AI-G020",
                "성능 신뢰구간 일부 누락",
                "핵심 성능지표의 confidence interval이 일부만 보고되었습니다.",
                "주요 보완",
                "AI-R007",
                "성능추정 정밀도 제한",
                "핵심 지표와 주요 subgroup에 95% confidence interval을 제시하십시오.",
            )
        )
    else:
        gaps.append(
            _gap(
                "AI-G021",
                "성능 신뢰구간 미보고",
                "Point estimate만으로는 모델성능의 통계적 불확실성을 판단할 수 없습니다.",
                "주요 보완",
                "AI-R007",
                "성능추정 정밀도 불명",
                "Sensitivity, specificity, PPV/NPV, AUROC/AUPRC에 신뢰구간을 보고하십시오.",
            )
        )

    if ai.decision_threshold is not None:
        score += 0.45
    else:
        gaps.append(
            _gap(
                "AI-G022",
                "Decision threshold 미보고",
                "양성·음성을 구분한 threshold와 선택근거가 확인되지 않았습니다.",
                "결정 제한",
                "AI-R008",
                "현재 예측 class의 재현성 제한",
                "Threshold, 선정목적 및 false-positive/false-negative trade-off를 보고하십시오.",
            )
        )

    if ai.external_validation == "확인됨":
        score += 0.55
    elif ai.external_validation == "부분적으로 확인":
        score += 0.25
    else:
        score += 0.0
    if ai.external_validation_representativeness == "현재 COU에 적절":
        score += 0.55
    elif ai.external_validation_representativeness == "부분적으로 적절":
        score += 0.25
    else:
        gaps.append(
            _gap(
                "AI-G023",
                "외부검증 집단 대표성 불충분",
                "외부검증 자료가 현재 modality, endpoint, 노출범위 또는 intended population을 대표하는지 불명확합니다.",
                "주요 보완",
                "AI-R009",
                "현재 Context of Use로의 일반화 제한",
                "외부검증 집단과 현재 후보의 modality, chemical space, endpoint 및 exposure를 비교하십시오.",
            )
        )

    if ai.positive_class_percent is not None and ai.positive_class_percent < 20 and ai.auprc is None:
        gaps.append(
            _gap(
                "AI-G024",
                "희귀 양성 class의 AUPRC 미보고",
                "양성 독성이 희귀한 데이터에서 AUROC 또는 accuracy만으로는 실용적 성능을 충분히 판단하기 어렵습니다.",
                "주요 보완",
                "AI-R007",
                "희귀 독성 탐지성능 불명",
                "Precision-recall curve와 AUPRC를 confidence interval과 함께 보고하십시오.",
            )
        )

    if ai.sensitivity_percent is not None and ai.false_negative_rate_percent is not None:
        expected_fnr = 100.0 - ai.sensitivity_percent
        if abs(expected_fnr - ai.false_negative_rate_percent) > 5.0:
            gaps.append(
                _gap(
                    "AI-G025",
                    "Sensitivity와 FNR 불일치",
                    "동일 dataset과 threshold라면 FNR은 일반적으로 100%-sensitivity와 일치해야 하나 입력값 차이가 큽니다.",
                    "결정 제한",
                    "AI-R010",
                    "성능표의 분모·threshold 또는 dataset 혼용 가능성",
                    "각 지표의 dataset, threshold, 분모 및 confidence interval을 대조하십시오.",
                )
            )
            score = min(score, 2.0)
    return _bounded(score)


def _calibration_adequacy(ai: AIModelCard, gaps: list[DataGap]) -> float | str:
    if ai.probability_percent is None:
        return "해당 없음"
    score = 0.0
    if ai.probability_type == "보정된 확률":
        score += 1.2
    elif ai.probability_type in {"원시 모델점수", "Ensemble agreement", "불명확"}:
        gaps.append(
            _gap(
                "AI-G026",
                "출력확률의 의미 불명확",
                "화면에 표시된 퍼센트가 calibrated probability인지 원시 score 또는 ensemble agreement인지 불명확합니다.",
                "결정 제한",
                "AI-R011",
                "예측값을 실제 독성확률로 표현할 수 없음",
                "출력값의 정의를 명시하고, 비보정 score에는 확률 또는 confidence라는 표현을 사용하지 마십시오.",
            )
        )
    calibration_scores = {
        "검증됨": 1.5,
        "부분 검증": 0.75,
        "미검증": 0.0,
        "불명확": 0.0,
    }
    score += calibration_scores.get(ai.calibration_status, 0.0)
    if ai.calibration_status in {"미검증", "불명확"}:
        gaps.append(
            _gap(
                "AI-G027",
                "Calibration 불충분",
                "모델 output과 실제 발생률의 일치가 검증되지 않았습니다.",
                "주요 보완",
                "AI-R011",
                "출력확률을 실제 위험확률로 해석할 수 없음",
                "Reliability curve, Brier score, calibration slope/intercept를 제시하십시오.",
            )
        )
    if ai.brier_score is not None:
        score += 0.45
    if ai.calibration_slope is not None and ai.calibration_intercept is not None:
        score += 0.55
    if ai.decision_threshold is not None:
        score += 0.3
    return _bounded(score)


def _lifecycle_governance(ai: AIModelCard, gaps: list[DataGap]) -> float:
    score = 0.0
    if ai.model_version:
        score += 0.4
    if ai.code_commit:
        score += 0.45
    if ai.software_environment:
        score += 0.4
    if ai.training_data_hash:
        score += 0.45
    if ai.last_validation_date:
        score += 0.35
    if ai.drift_monitoring == "운영 중":
        score += 0.8
    elif ai.drift_monitoring == "계획 있음":
        score += 0.4
    if ai.change_control == "정의됨":
        score += 0.65
    elif ai.change_control == "부분 정의":
        score += 0.3
    if ai.lifecycle_plan == "정의됨":
        score += 0.5
    elif ai.lifecycle_plan == "부분 정의":
        score += 0.25

    if not ai.code_commit or not ai.software_environment or not ai.training_data_hash:
        gaps.append(
            _gap(
                "AI-G028",
                "재현성 메타데이터 불완전",
                "Code commit, software environment 또는 training-data hash 중 하나 이상이 없습니다.",
                "주요 보완",
                "AI-R012",
                "동일 예측의 재생산과 변경영향 추적 제한",
                "Code commit, package/environment lock 및 dataset hash를 함께 기록하십시오.",
            )
        )
    if ai.drift_monitoring == "없음" or ai.change_control == "불명확" or ai.lifecycle_plan == "없음":
        gaps.append(
            _gap(
                "AI-G029",
                "Lifecycle·Drift 관리 불충분",
                "모델 성능저하, data/concept drift, threshold 변경 및 재검증을 관리하는 절차가 충분하지 않습니다.",
                "주요 보완",
                "AI-R012",
                "R4/R5와 장기 운영 적합성 제한",
                "Drift trigger, change control, 재검증 기준 및 과거 평가 재실행 절차를 정의하십시오.",
            )
        )
    return _bounded(score)


def _prediction_reliability(
    inp: AssessmentInput,
    data_score: float,
    ground_truth_score: float,
    performance_score: float,
    calibration_score: float | str,
    candidate_applicability: float,
    lifecycle_score: float,
    gaps: list[DataGap],
) -> tuple[float, str]:
    ai = inp.ai_model
    values = [data_score, ground_truth_score, performance_score, candidate_applicability, lifecycle_score]
    if isinstance(calibration_score, float):
        values.append(calibration_score)
    score = _bounded(_average(values))

    if candidate_applicability <= 0.6:
        score = min(score, 0.5)
    elif candidate_applicability <= 1.2:
        score = min(score, 1.0)
    if ai.test_set_independence == "비독립 / 중복 확인" or ai.leakage_assessment == "누수 확인":
        score = min(score, 0.8)
    elif ai.leakage_assessment == "누수 가능성":
        score = min(score, 1.5)
    if ai.result == "음성 / 낮은 위험 예측" and ai.false_negative_rate_percent is None:
        score = min(score, 2.0)
    if ai.prediction_uncertainty in {"높음", "불명확"}:
        score = min(score, 2.0 if ai.prediction_uncertainty == "불명확" else 1.5)
    if not ai.input_quality_verified:
        score = min(score, 2.0)
        gaps.append(
            _gap(
                "AI-G030",
                "개별 예측 입력 품질 미검증",
                "구조, 염형, 이성질체, 서열, 제형 또는 입력 feature가 현재 후보를 정확히 표현하는지 확인되지 않았습니다.",
                "결정 제한",
                "AI-R013",
                "개별 prediction reliability 최대 중간",
                "예측 입력의 identity, structure/sequence normalization 및 batch/formulation 정보를 확인하십시오.",
            )
        )
    if ai.ood_detection in {"없음", "불명확"}:
        gaps.append(
            _gap(
                "AI-G031",
                "OOD 탐지 근거 부족",
                "개별 후보가 학습분포 밖에 있는지 탐지하는 정량적 근거가 부족합니다.",
                "주요 보완",
                "AI-R014",
                "Applicability 판단의 객관성 제한",
                "Nearest-neighbor distance, leverage, domain density 또는 별도 OOD detector를 보고하십시오.",
            )
        )
    if ai.explainability_status in {"없음", "불명확"} or ai.biological_plausibility in {"불명확", "낮음"}:
        gaps.append(
            _gap(
                "AI-G032",
                "생물학적 설명가능성 제한",
                "모델이 강조한 feature가 알려진 독성기전, 제품 특성 및 관찰 가능한 endpoint와 충분히 연결되지 않았습니다.",
                "주요 보완",
                "AI-R015",
                "기전적 해석과 후속시험 설계 제한",
                "Prediction explanation을 알려진 독성기전 및 orthogonal NAM endpoint와 연결하십시오.",
            )
        )
    if score >= 3.2:
        label = "높음"
    elif score >= 2.2:
        label = "중간"
    elif score >= 1.0:
        label = "낮음"
    else:
        label = "평가 불가"
    return _bounded(score), label


def assess_ai_credibility(inp: AssessmentInput, candidate_applicability: float) -> AICredibilityResult:
    ai = inp.ai_model
    if not ai.use_ai:
        return AICredibilityResult(
            data_credibility=0.0,
            ground_truth_adequacy=0.0,
            performance_adequacy=0.0,
            calibration_adequacy="해당 없음",
            prediction_reliability_score=0.0,
            prediction_reliability_label="해당 없음",
            lifecycle_governance=0.0,
            gaps=(),
            gates=(),
        )

    gaps: list[DataGap] = []
    data = _data_credibility(ai, gaps)
    ground = _ground_truth_adequacy(ai, gaps)
    performance = _performance_adequacy(ai, gaps)
    calibration = _calibration_adequacy(ai, gaps)
    lifecycle = _lifecycle_governance(ai, gaps)
    prediction_score, prediction_label = _prediction_reliability(
        inp,
        data,
        ground,
        performance,
        calibration,
        candidate_applicability,
        lifecycle,
        gaps,
    )

    leakage_pass = ai.leakage_assessment == "평가 완료 — 문제 없음" and ai.test_set_independence == "독립 확인"
    calibration_pass = (
        ai.probability_percent is None
        or (ai.probability_type == "보정된 확률" and ai.calibration_status in {"검증됨", "부분 검증"})
    )
    gates = (
        GateResult(
            "Endpoint·Ground Truth",
            "통과" if ground >= 3.0 else "미통과" if ground < 2.0 else "조건부",
            "Endpoint 정의, reference standard, label 품질, missing-label 정책을 확인합니다.",
            "낮으면 Evidence Role R2 이하",
        ),
        GateResult(
            "데이터 독립성·Leakage",
            "통과" if leakage_pass else "미통과" if ai.leakage_assessment in {"누수 확인", "누수 가능성"} or ai.test_set_independence == "비독립 / 중복 확인" else "조건부",
            "학습·시험자료 독립성과 전처리·feature leakage를 확인합니다.",
            "Leakage 또는 비독립 검증은 R1 이하",
        ),
        GateResult(
            "예측성능·불확실성",
            "통과" if performance >= 3.0 else "조건부" if performance >= 2.0 else "미통과",
            "Sensitivity, specificity, predictive values, threshold, AUPRC 및 confidence interval을 확인합니다.",
            "낮으면 고영향 음성·양성 해석 제한",
        ),
        GateResult(
            "확률 Calibration",
            "통과" if calibration_pass else "미통과",
            "표시된 퍼센트가 calibrated probability인지 확인합니다.",
            "미통과 시 실제 위험확률 표현 금지",
        ),
        GateResult(
            "개별 예측 신뢰성",
            "통과" if prediction_score >= 3.0 else "조건부" if prediction_score >= 2.0 else "미통과",
            "현재 후보의 입력품질, domain fit, OOD 및 prediction uncertainty를 확인합니다.",
            "낮으면 Reliable Negative/Positive 불인정",
        ),
        GateResult(
            "AI Lifecycle·Governance",
            "통과" if lifecycle >= 3.0 else "조건부" if lifecycle >= 2.0 else "미통과",
            "Version, code, data hash, drift monitoring 및 change control을 확인합니다.",
            "낮으면 R4/R5와 반복사용 제한",
        ),
    )
    return AICredibilityResult(
        data_credibility=data,
        ground_truth_adequacy=ground,
        performance_adequacy=performance,
        calibration_adequacy=calibration,
        prediction_reliability_score=prediction_score,
        prediction_reliability_label=prediction_label,
        lifecycle_governance=lifecycle,
        gaps=tuple(gaps),
        gates=gates,
    )
