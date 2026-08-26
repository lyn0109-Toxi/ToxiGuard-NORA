from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ContextOfUse:
    objective: str = "동물시험 범위 축소 가능성 평가"
    question_of_interest: str = ""
    development_stage: str = "후보물질 선정"
    target_endpoint: str = "초기 간독성"
    intended_evidence_role: str = "R4 · 동물시험 축소 지원"
    jurisdiction: str = "연구용 / 내부 의사결정"
    model_influence: int = 3
    decision_consequence: int = 3
    decision_owner: str = ""


@dataclass
class ProductContext:
    product_name: str = ""
    modality: str = "siRNA + 나노의약품"
    indication: str = ""
    active_substance: str = ""
    target_mechanism: str = ""
    carrier_formulation: str = ""
    route: str = "정맥투여"
    planned_dose: str = ""
    exposure_pattern: str = "반복 노출"
    frequency: str = ""
    treatment_duration: str = ""
    target_organs: str = "간, 비장"
    human_cmax: str = ""
    human_auc: str = ""
    distribution_status: str = "정성적 자료"
    test_article_representativeness: str = "불명확"


@dataclass
class AIModelCard:
    use_ai: bool = True
    model_name: str = ""
    model_version: str = ""
    model_type: str = "Machine learning classifier"
    endpoint: str = "초기 간독성"
    result: str = "음성 / 낮은 위험 예측"
    probability_percent: float | None = None
    domain_modalities: list[str] = field(default_factory=lambda: ["저분자"])
    external_validation: str = "부분적으로 확인"
    sensitivity_percent: float | None = None
    specificity_percent: float | None = None
    false_negative_rate_percent: float | None = None
    calibration_status: str = "불명확"
    domain_status: str = "자동 평가"
    source: str = ""
    known_limitations: str = ""


@dataclass
class NAMAssayCard:
    use_nam: bool = True
    nam_type: str = "2D 세포시험"
    system_origin: str = "사람 유래"
    result: str = "음성"
    cell_types: list[str] = field(default_factory=lambda: ["간세포(Hepatocyte)"])
    metabolic_competence: str = "부분 확인"
    immune_competence: str = "미포함 / 불명확"
    exposure_design: str = "단회/급성 노출"
    positive_control: str = "유효"
    negative_control: str = "유효"
    carrier_only_control: str = "미포함"
    active_only_control: str = "미포함"
    protocol_completeness: str = "부분적"
    nominal_exposure: str = ""
    measured_exposure: str = "측정 안 됨"
    qivive_pbpk: str = "없음"
    reproducibility: str = "일부 확인"
    endpoints: list[str] = field(default_factory=lambda: ["Cell viability / ATP"])


@dataclass
class SupportingEvidence:
    mechanistic_evidence: bool = False
    class_or_clinical_evidence: bool = False
    quantitative_biodistribution: bool = False
    pk_tk_evidence: bool = False
    existing_in_vivo_evidence: bool = False
    human_evidence: bool = False
    evidence_traceable: bool = True
    assertions_reviewed: bool = False
    expert_reviewed: bool = False
    version_locked: bool = True
    expert_review_note: str = ""
    supporting_note: str = ""


@dataclass
class AssessmentInput:
    context_of_use: ContextOfUse = field(default_factory=ContextOfUse)
    product: ProductContext = field(default_factory=ProductContext)
    ai_model: AIModelCard = field(default_factory=AIModelCard)
    nam_assay: NAMAssayCard = field(default_factory=NAMAssayCard)
    supporting_evidence: SupportingEvidence = field(default_factory=SupportingEvidence)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AssessmentInput":
        return cls(
            context_of_use=ContextOfUse(**payload.get("context_of_use", {})),
            product=ProductContext(**payload.get("product", {})),
            ai_model=AIModelCard(**payload.get("ai_model", {})),
            nam_assay=NAMAssayCard(**payload.get("nam_assay", {})),
            supporting_evidence=SupportingEvidence(**payload.get("supporting_evidence", {})),
        )


@dataclass(frozen=True)
class DataGap:
    code: str
    title: str
    description: str
    criticality: str
    rule_id: str
    effect: str
    recommendation: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class GateResult:
    gate: str
    status: str
    rationale: str
    effect: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass
class AssessmentResult:
    evidence_role: int
    evidence_role_code: str
    evidence_role_name: str
    evidence_role_description: str
    animal_use_status: str
    animal_use_description: str
    model_risk: str
    residual_uncertainty: str
    evidence_stream_count: int
    scores: dict[str, float | str]
    gates: list[GateResult]
    data_gaps: list[DataGap]
    observations: list[str]
    interpretations: list[str]
    development_relevance: list[str]
    recommendations: list[str]
    audit: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_role": self.evidence_role,
            "evidence_role_code": self.evidence_role_code,
            "evidence_role_name": self.evidence_role_name,
            "evidence_role_description": self.evidence_role_description,
            "animal_use_status": self.animal_use_status,
            "animal_use_description": self.animal_use_description,
            "model_risk": self.model_risk,
            "residual_uncertainty": self.residual_uncertainty,
            "evidence_stream_count": self.evidence_stream_count,
            "scores": self.scores,
            "gates": [g.to_dict() for g in self.gates],
            "data_gaps": [g.to_dict() for g in self.data_gaps],
            "observations": self.observations,
            "interpretations": self.interpretations,
            "development_relevance": self.development_relevance,
            "recommendations": self.recommendations,
            "audit": self.audit,
        }
