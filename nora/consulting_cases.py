"""Customer-objective consulting case library for ToxiGuard NORA.

The core EarlyTox engine remains limited to the early-hepatotoxicity vertical
slice.  ConsultingCase metadata deliberately separates the engine's Evidence
Role from the advisor's Development Concern so that a credible positive signal
is not misread as a low-risk or animal-reduction recommendation.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Callable

from .cases import concordant_case, conflicting_case, gp_l_ct_case
from .models import AIModelCard, AssessmentInput, ContextOfUse, NAMAssayCard, ProductContext, SupportingEvidence


@dataclass(frozen=True)
class ConsultingCase:
    case_id: str
    title_ko: str
    title_en: str
    customer_segment_ko: str
    customer_segment_en: str
    primary_objective_ko: str
    primary_objective_en: str
    engagement_type_ko: str
    engagement_type_en: str
    trigger_ko: str
    trigger_en: str
    decision_question_ko: str
    decision_question_en: str
    development_concern_ko: str
    development_concern_en: str
    automation_scope_ko: str
    automation_scope_en: str
    deliverables_ko: tuple[str, ...]
    deliverables_en: tuple[str, ...]
    recommended_actions_ko: tuple[str, ...]
    recommended_actions_en: tuple[str, ...]
    service_tier_ko: str
    service_tier_en: str
    commercial_model_ko: str
    commercial_model_en: str
    regulatory_anchors: tuple[str, ...] = field(default_factory=tuple)
    assessment_builder: Callable[[], AssessmentInput] | None = None
    expected_role_min: int | None = None
    expected_role_max: int | None = None
    related_case_ids: tuple[str, ...] = field(default_factory=tuple)
    asset_ko: str = ""
    asset_en: str = ""
    case_basis_ko: str = ""
    case_basis_en: str = ""
    public_evidence_ko: tuple[str, ...] = field(default_factory=tuple)
    public_evidence_en: tuple[str, ...] = field(default_factory=tuple)
    synthetic_assumptions_ko: tuple[str, ...] = field(default_factory=tuple)
    synthetic_assumptions_en: tuple[str, ...] = field(default_factory=tuple)
    advisory_inferences_ko: tuple[str, ...] = field(default_factory=tuple)
    advisory_inferences_en: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_engine_supported(self) -> bool:
        return self.assessment_builder is not None

    def title(self, language: str = "ko") -> str:
        return self.title_en if language == "en" else self.title_ko

    def customer_segment(self, language: str = "ko") -> str:
        return self.customer_segment_en if language == "en" else self.customer_segment_ko

    def primary_objective(self, language: str = "ko") -> str:
        return self.primary_objective_en if language == "en" else self.primary_objective_ko

    def engagement_type(self, language: str = "ko") -> str:
        return self.engagement_type_en if language == "en" else self.engagement_type_ko

    def trigger(self, language: str = "ko") -> str:
        return self.trigger_en if language == "en" else self.trigger_ko

    def decision_question(self, language: str = "ko") -> str:
        return self.decision_question_en if language == "en" else self.decision_question_ko

    def development_concern(self, language: str = "ko") -> str:
        return self.development_concern_en if language == "en" else self.development_concern_ko

    def automation_scope(self, language: str = "ko") -> str:
        return self.automation_scope_en if language == "en" else self.automation_scope_ko

    def deliverables(self, language: str = "ko") -> tuple[str, ...]:
        return self.deliverables_en if language == "en" else self.deliverables_ko

    def recommended_actions(self, language: str = "ko") -> tuple[str, ...]:
        return self.recommended_actions_en if language == "en" else self.recommended_actions_ko

    def service_tier(self, language: str = "ko") -> str:
        return self.service_tier_en if language == "en" else self.service_tier_ko

    def commercial_model(self, language: str = "ko") -> str:
        return self.commercial_model_en if language == "en" else self.commercial_model_ko

    def asset(self, language: str = "ko") -> str:
        return self.asset_en if language == "en" else self.asset_ko

    def case_basis(self, language: str = "ko") -> str:
        return self.case_basis_en if language == "en" else self.case_basis_ko

    def public_evidence(self, language: str = "ko") -> tuple[str, ...]:
        return self.public_evidence_en if language == "en" else self.public_evidence_ko

    def synthetic_assumptions(self, language: str = "ko") -> tuple[str, ...]:
        return self.synthetic_assumptions_en if language == "en" else self.synthetic_assumptions_ko

    def advisory_inferences(self, language: str = "ko") -> tuple[str, ...]:
        return self.advisory_inferences_en if language == "en" else self.advisory_inferences_ko


def _ai_vendor_validation_case() -> AssessmentInput:
    return AssessmentInput(
        context_of_use=ContextOfUse(
            objective="AI 독성예측 결과 검증",
            question_of_interest="외부 AI 모델의 음성 간독성 예측을 lead-selection 회의에서 어느 범위까지 사용할 수 있는가?",
            development_stage="후보물질 선정",
            target_endpoint="초기 간독성",
            intended_evidence_role="R2 · 초기 선별",
            jurisdiction="연구용 / 내부 의사결정",
            model_influence=3,
            decision_consequence=3,
            decision_owner="Discovery toxicology lead",
        ),
        product=ProductContext(
            product_name="SM-Lead-27",
            modality="저분자 NME",
            indication="염증성 질환",
            active_substance="Selective kinase inhibitor",
            target_mechanism="Kinase-X inhibition",
            route="경구",
            planned_dose="10–100 mg/day",
            exposure_pattern="반복 노출",
            frequency="1일 1회",
            treatment_duration="14일",
            target_organs="간",
            distribution_status="정성적 자료",
            test_article_representativeness="부분적으로 확인",
        ),
        ai_model=AIModelCard(
            use_ai=True,
            model_name="Vendor DILI Predictor",
            model_version="2026.1",
            model_type="Graph neural network",
            endpoint="초기 간독성",
            result="음성 / 낮은 위험 예측",
            probability_percent=18,
            probability_type="보정된 확률",
            endpoint_definition="Vendor-defined early DILI binary endpoint",
            reference_standard="문헌 / 라벨 기반",
            label_quality="단일 출처 / 자동 라벨",
            missing_label_policy="일부 구분",
            time_window_defined=True,
            severity_threshold_defined=False,
            dataset_source="Vendor curated dataset",
            dataset_version="2026.1",
            training_sample_size=2100,
            positive_class_percent=12.0,
            split_strategy="Scaffold 분할",
            test_set_independence="부분 확인",
            leakage_assessment="일부 확인",
            duplicate_assessment="중복 제거 / 관리",
            domain_modalities=["저분자"],
            external_validation="부분적으로 확인",
            external_validation_representativeness="부분적으로 적절",
            sensitivity_percent=79,
            specificity_percent=81,
            false_negative_rate_percent=None,
            false_positive_rate_percent=19,
            ppv_percent=52,
            npv_percent=None,
            balanced_accuracy_percent=80,
            auroc=0.83,
            auprc=0.49,
            performance_confidence_intervals="부분 보고",
            decision_threshold=0.45,
            calibration_status="부분 검증",
            brier_score=0.16,
            calibration_slope=None,
            calibration_intercept=None,
            domain_status="Borderline",
            nearest_neighbor_similarity_percent=58,
            ood_detection="정량 평가 — In-domain",
            prediction_interval="12–31%",
            prediction_uncertainty="중간",
            input_quality_verified=True,
            explainability_status="부분 연결",
            biological_plausibility="중간",
            source="Vendor model card",
            known_limitations="Novel scaffold near the boundary; limited metabolite representation",
            code_commit="vendor-build-2026.1",
            software_environment="Vendor-managed environment",
            training_data_hash="vendor-signed-dataset-hash",
            last_validation_date="2026-05-20",
            drift_monitoring="계획 있음",
            change_control="부분 정의",
            lifecycle_plan="부분 정의",
        ),
        nam_assay=NAMAssayCard(
            use_nam=True,
            nam_type="2D 세포시험",
            system_origin="사람 유래",
            result="음성",
            cell_types=["간세포(Hepatocyte)"],
            metabolic_competence="부분 확인",
            immune_competence="미포함 / 불명확",
            exposure_design="단회/급성 노출",
            positive_control="유효",
            negative_control="유효",
            carrier_only_control="해당 없음",
            active_only_control="해당 없음",
            protocol_completeness="부분적",
            nominal_exposure="0.1–30 µM",
            measured_exposure="부분 측정",
            qivive_pbpk="없음",
            reproducibility="일부 확인",
            endpoints=["Cell viability / ATP", "미토콘드리아 기능"],
        ),
        supporting_evidence=SupportingEvidence(
            mechanistic_evidence=True,
            evidence_traceable=True,
            assertions_reviewed=True,
            expert_reviewed=False,
            version_locked=True,
            supporting_note="Vendor model review before candidate selection.",
        ),
    )


def _candidate_comparison_case() -> AssessmentInput:
    case = deepcopy(concordant_case())
    case.context_of_use.objective = "후보물질 비교"
    case.context_of_use.question_of_interest = (
        "세 후보 중 어떤 후보가 간독성 근거의 신뢰도, 사람 관련성 및 개발여유 측면에서 우선순위가 높은가?"
    )
    case.context_of_use.intended_evidence_role = "R3 · 보조 근거"
    case.context_of_use.decision_owner = "Candidate-selection committee"
    case.product.product_name = "Lead-B"
    case.product.indication = "자가면역질환"
    case.supporting_evidence.expert_reviewed = False
    case.supporting_evidence.expert_review_note = ""
    return case


def _animal_reduction_case() -> AssessmentInput:
    case = deepcopy(concordant_case())
    case.product.product_name = "VB-NME-04"
    case.context_of_use.question_of_interest = (
        "현재 AI/NAM 패키지가 계획된 반복투여시험의 용량군과 중복 간 endpoint를 제한적으로 줄이는 데 충분한가?"
    )
    case.context_of_use.decision_owner = "Virtual biotech toxicology lead"
    return case


def _gene_therapy_positive_case() -> AssessmentInput:
    return AssessmentInput(
        context_of_use=ContextOfUse(
            objective="AI·NAM·기존 근거 통합",
            question_of_interest=(
                "AAV 기반 유전자치료제의 간 tropism과 양성 human NAM 신호가 개발위험 및 추가 in vivo 범위에 어떤 의미가 있는가?"
            ),
            development_stage="초기 비임상 개발",
            target_endpoint="초기 간독성",
            intended_evidence_role="R3 · 보조 근거",
            jurisdiction="미국 FDA 사전미팅 준비",
            model_influence=2,
            decision_consequence=5,
            decision_owner="Gene therapy toxicology lead",
        ),
        product=ProductContext(
            product_name="GT-AAV-05",
            modality="바이오의약품",
            indication="희귀 유전질환",
            active_substance="AAV vector carrying therapeutic gene",
            target_mechanism="Liver-directed gene expression",
            carrier_formulation="AAV8 capsid",
            route="정맥투여",
            planned_dose="1×10^13 vg/kg",
            exposure_pattern="단회 노출",
            frequency="1회",
            treatment_duration="단회",
            target_organs="간",
            human_cmax="해당 없음",
            human_auc="Vector-genome exposure surrogate",
            distribution_status="정량적 자료",
            test_article_representativeness="임상제품 대표성 확인",
        ),
        ai_model=AIModelCard(use_ai=False),
        nam_assay=NAMAssayCard(
            use_nam=True,
            nam_type="간 Organoid",
            system_origin="사람 유래",
            result="양성",
            cell_types=["간세포(Hepatocyte)", "Kupffer cell", "간 내피세포"],
            metabolic_competence="충분히 확인",
            immune_competence="충분",
            exposure_design="지속노출",
            positive_control="유효",
            negative_control="유효",
            carrier_only_control="해당 없음",
            active_only_control="해당 없음",
            protocol_completeness="완결",
            nominal_exposure="Dose-response by vg/cell",
            measured_exposure="측정됨",
            qivive_pbpk="초기 연결",
            reproducibility="Donor/lot/반복 재현성 확인",
            endpoints=["Cell viability / ATP", "ALT / AST / GLDH", "Cytokine", "Omics signature"],
        ),
        supporting_evidence=SupportingEvidence(
            mechanistic_evidence=True,
            class_or_clinical_evidence=True,
            quantitative_biodistribution=True,
            pk_tk_evidence=True,
            existing_in_vivo_evidence=True,
            human_evidence=True,
            evidence_traceable=True,
            assertions_reviewed=True,
            expert_reviewed=False,
            version_locked=True,
            supporting_note="A credible positive signal is present; animal reduction is not the primary decision.",
        ),
    )


def _mab_streamlining_case() -> AssessmentInput:
    return AssessmentInput(
        context_of_use=ContextOfUse(
            objective="동물시험 범위 축소 가능성 평가",
            question_of_interest=(
                "단일 표적 mAb의 human-relevant pharmacology와 반복노출 NAM이 불필요한 장기 NHP 시험 범위를 줄이는 데 충분한가?"
            ),
            development_stage="초기 비임상 개발",
            target_endpoint="초기 간독성",
            intended_evidence_role="R4 · 동물시험 축소 지원",
            jurisdiction="미국 FDA 사전미팅 준비",
            model_influence=2,
            decision_consequence=4,
            decision_owner="Biologics safety lead",
        ),
        product=ProductContext(
            product_name="mAb-ONC-06",
            modality="바이오의약품",
            indication="고형암",
            active_substance="Humanized monospecific antibody",
            target_mechanism="Target-Y blockade",
            carrier_formulation="IV infusion formulation",
            route="정맥투여",
            planned_dose="1–10 mg/kg",
            exposure_pattern="반복 노출",
            frequency="2주 간격",
            treatment_duration="12주",
            target_organs="간, 면역계",
            human_cmax="Model-predicted",
            human_auc="Model-predicted",
            distribution_status="정량적 자료",
            test_article_representativeness="임상제품 대표성 확인",
        ),
        ai_model=AIModelCard(use_ai=False),
        nam_assay=NAMAssayCard(
            use_nam=True,
            nam_type="공배양(Coculture)",
            system_origin="사람 유래",
            result="음성",
            cell_types=["간세포(Hepatocyte)", "Kupffer cell", "간 내피세포"],
            metabolic_competence="충분히 확인",
            immune_competence="충분",
            exposure_design="반복노출",
            positive_control="유효",
            negative_control="유효",
            carrier_only_control="해당 없음",
            active_only_control="해당 없음",
            protocol_completeness="완결",
            nominal_exposure="0.1–20× clinical Cmax",
            measured_exposure="측정됨",
            qivive_pbpk="수행됨",
            reproducibility="Donor/lot/반복 재현성 확인",
            endpoints=["Cell viability / ATP", "ALT / AST / GLDH", "Cytokine", "미토콘드리아 기능"],
        ),
        supporting_evidence=SupportingEvidence(
            mechanistic_evidence=True,
            class_or_clinical_evidence=True,
            quantitative_biodistribution=True,
            pk_tk_evidence=True,
            existing_in_vivo_evidence=True,
            human_evidence=True,
            evidence_traceable=True,
            assertions_reviewed=True,
            expert_reviewed=True,
            version_locked=True,
            expert_review_note="Limit reduction to duplicate long-term endpoints; maintain targeted in vivo monitoring.",
        ),
    )


def _cro_protocol_review_case() -> AssessmentInput:
    return AssessmentInput(
        context_of_use=ContextOfUse(
            objective="다음 비임상시험 설계",
            question_of_interest="CRO가 제안한 28일 반복투여 독성시험 설계가 간독성, 노출 및 회복성 질문에 답할 수 있는가?",
            development_stage="초기 비임상 개발",
            target_endpoint="초기 간독성",
            intended_evidence_role="R3 · 보조 근거",
            jurisdiction="연구용 / 내부 의사결정",
            model_influence=1,
            decision_consequence=4,
            decision_owner="Sponsor study monitor",
        ),
        product=ProductContext(
            product_name="CRO-Protocol-07",
            modality="저분자 NME",
            indication="자가면역질환",
            active_substance="NME-07",
            target_mechanism="Immune pathway modulator",
            route="경구",
            planned_dose="3 dose groups",
            exposure_pattern="반복 노출",
            frequency="1일 1회",
            treatment_duration="28일",
            target_organs="간",
            distribution_status="정성적 자료",
            test_article_representativeness="부분적으로 확인",
        ),
        ai_model=AIModelCard(
            use_ai=True,
            model_name="Internal DILI screen",
            model_version="v1.8",
            endpoint="초기 간독성",
            result="경계 / 불확실",
            probability_type="불명확",
            endpoint_definition="Internal exploratory hepatotoxicity alert",
            reference_standard="문헌 / 라벨 기반",
            label_quality="단일 출처 / 자동 라벨",
            missing_label_policy="불명확",
            time_window_defined=False,
            severity_threshold_defined=False,
            dataset_source="Internal exploratory dataset",
            dataset_version="v1.8",
            training_sample_size=480,
            positive_class_percent=None,
            split_strategy="무작위 분할",
            test_set_independence="불명확",
            leakage_assessment="미평가",
            duplicate_assessment="미평가",
            domain_modalities=["저분자"],
            external_validation="부분적으로 확인",
            external_validation_representativeness="불명확",
            sensitivity_percent=75,
            specificity_percent=70,
            false_negative_rate_percent=25,
            false_positive_rate_percent=30,
            ppv_percent=None,
            npv_percent=None,
            balanced_accuracy_percent=72.5,
            auroc=0.74,
            auprc=None,
            performance_confidence_intervals="불명확",
            decision_threshold=None,
            calibration_status="불명확",
            brier_score=None,
            calibration_slope=None,
            calibration_intercept=None,
            domain_status="In-domain",
            nearest_neighbor_similarity_percent=None,
            ood_detection="불명확",
            prediction_interval="",
            prediction_uncertainty="불명확",
            input_quality_verified=False,
            explainability_status="불명확",
            biological_plausibility="불명확",
            source="Internal report",
            code_commit="",
            software_environment="",
            training_data_hash="",
            last_validation_date="",
            drift_monitoring="없음",
            change_control="불명확",
            lifecycle_plan="없음",
        ),
        nam_assay=NAMAssayCard(
            use_nam=True,
            nam_type="2D 세포시험",
            system_origin="사람 유래",
            result="음성",
            cell_types=["간세포(Hepatocyte)"],
            metabolic_competence="부분 확인",
            immune_competence="미포함 / 불명확",
            exposure_design="단회/급성 노출",
            positive_control="없음 / 불명확",
            negative_control="유효",
            carrier_only_control="해당 없음",
            active_only_control="해당 없음",
            protocol_completeness="불충분",
            nominal_exposure="미정",
            measured_exposure="측정 안 됨",
            qivive_pbpk="없음",
            reproducibility="확인되지 않음",
            endpoints=["Cell viability / ATP"],
        ),
        supporting_evidence=SupportingEvidence(
            mechanistic_evidence=True,
            evidence_traceable=True,
            assertions_reviewed=True,
            expert_reviewed=False,
            version_locked=True,
        ),
    )


def _license_in_due_diligence_case() -> AssessmentInput:
    case = deepcopy(conflicting_case())
    case.context_of_use.objective = "외부도입 후보 평가"
    case.context_of_use.question_of_interest = (
        "외부도입 후보의 AI 음성예측과 human organoid 양성신호가 거래가치, 계약조건 및 추가 실사 범위에 어떤 영향을 주는가?"
    )
    case.context_of_use.decision_owner = "Business development / toxicology review team"
    case.product.product_name = "LIC-IN-08"
    return case


def _preind_meeting_case() -> AssessmentInput:
    case = deepcopy(concordant_case())
    case.context_of_use.objective = "CTA/IND 준비도 확인"
    case.context_of_use.question_of_interest = (
        "Pre-IND meeting package에서 AI/NAM 간독성 근거를 어떤 역할로 제시하고 FDA에 어떤 질문을 해야 하는가?"
    )
    case.context_of_use.jurisdiction = "미국 FDA 사전미팅 준비"
    case.context_of_use.intended_evidence_role = "R3 · 보조 근거"
    case.context_of_use.decision_owner = "Regulatory strategy lead"
    case.product.product_name = "PREIND-09"
    case.supporting_evidence.expert_reviewed = False
    case.supporting_evidence.expert_review_note = ""
    return case


def _comparability_bridge_case() -> AssessmentInput:
    case = deepcopy(concordant_case())
    case.context_of_use.objective = "임상제품 비교가능성 평가"
    case.context_of_use.question_of_interest = (
        "독성시험 배치와 변경된 임상제형 간 CQA 차이가 기존 간독성 근거의 사용 가능성과 추가 bridging 전략에 미치는 영향은 무엇인가?"
    )
    case.context_of_use.intended_evidence_role = "R3 · 보조 근거"
    case.context_of_use.decision_owner = "CMC / toxicology joint review team"
    case.product.product_name = "NANO-COMP-10"
    case.product.modality = "나노의약품"
    case.product.carrier_formulation = "Reformulated lipid nanoparticle"
    case.product.test_article_representativeness = "불명확"
    case.ai_model.domain_modalities = ["나노의약품"]
    case.nam_assay.carrier_only_control = "포함"
    case.supporting_evidence.expert_reviewed = False
    case.supporting_evidence.expert_review_note = ""
    return case


CONSULTING_CASES: dict[str, ConsultingCase] = {
    "LAB-001": ConsultingCase(
        case_id="LAB-001",
        title_ko="대학 연구실 — 동물시험 전 초기 독성질문 설계",
        title_en="Academic lab — Early toxicity question framing before animal work",
        customer_segment_ko="대학·연구기관",
        customer_segment_en="Academic / research institution",
        primary_objective_ko="초기 위험지도와 다음 시험 우선순위",
        primary_objective_en="Early hazard map and next-study priorities",
        engagement_type_ko="Discovery Toxicity Mapping Sprint",
        engagement_type_en="Discovery Toxicity Mapping Sprint",
        trigger_ko="약효 POC는 있으나 독성개발 경험과 예산이 제한됨",
        trigger_en="Efficacy proof of concept exists, but toxicology experience and budget are limited",
        decision_question_ko="GP-L-CT와 같은 siRNA 나노입자에서 무엇을 먼저 확인해야 불필요한 동물시험을 피할 수 있는가?",
        decision_question_en="What should be tested first for an siRNA nanomedicine such as GP-L-CT to avoid poorly targeted animal work?",
        development_concern_ko="미정 — 근거 부족과 적용범위 이탈로 위험을 낮게 분류할 수 없음",
        development_concern_en="Unknown — insufficient and out-of-domain evidence prevents a low-concern conclusion",
        automation_scope_ko="EarlyTox 엔진으로 자동평가 가능",
        automation_scope_en="Supported by the EarlyTox engine",
        deliverables_ko=("제품-위험-독성질문 맵", "최소 NAM/노출 패키지", "동물시험 전 Go/Refine/Hold 체크포인트"),
        deliverables_en=("Product–hazard–toxicity-question map", "Minimum NAM/exposure package", "Pre-animal Go/Refine/Hold checkpoints"),
        recommended_actions_ko=("정량적 간·비장 분포", "Kupffer cell 포함 반복노출 NAM", "Carrier-only 및 active-only 대조군"),
        recommended_actions_en=("Quantitative liver/spleen distribution", "Repeated-exposure NAM with Kupffer cells", "Carrier-only and active-only controls"),
        service_tier_ko="진단형 — 데이터 갭 분석",
        service_tier_en="Diagnostic — Data-gap analysis",
        commercial_model_ko="내부 가격기획 기준: 프로젝트당 $5k–$15k 범주",
        commercial_model_en="Internal pricing reference: project band of $5k–$15k",
        regulatory_anchors=("FDA-NAM-2026-DRAFT", "FDA-AI-2025-DRAFT", "OECD-GIVIMP-2025"),
        assessment_builder=gp_l_ct_case,
        expected_role_min=1,
        expected_role_max=1,
    ),
    "AI-002": ConsultingCase(
        case_id="AI-002",
        title_ko="초기 바이오텍 — 외부 AI 독성모델 구매 전 검증",
        title_en="Early biotech — Credibility review before relying on a vendor AI model",
        customer_segment_ko="초기 바이오텍",
        customer_segment_en="Early-stage biotech",
        primary_objective_ko="AI 결과의 의사결정 사용범위 설정",
        primary_objective_en="Define the decision-use boundary of an AI result",
        engagement_type_ko="AI Model Credibility Review",
        engagement_type_en="AI Model Credibility Review",
        trigger_ko="Vendor가 낮은 DILI 위험을 제시했지만 학습범위와 false-negative 성능이 불명확",
        trigger_en="A vendor reports low DILI risk, but applicability and false-negative performance are unclear",
        decision_question_ko="이 음성예측을 후보선정 근거로 쓸 수 있는가?",
        decision_question_en="Can this negative prediction be used in candidate selection?",
        development_concern_ko="미정 — 선별에는 사용 가능하지만 안전결론에는 부족",
        development_concern_en="Unknown — usable for screening, insufficient for a safety conclusion",
        automation_scope_ko="EarlyTox 엔진으로 자동평가 가능",
        automation_scope_en="Supported by the EarlyTox engine",
        deliverables_ko=("Model Card 독립 검토", "COU와 Model Risk 정의", "Vendor 보완질문 목록"),
        deliverables_en=("Independent model-card review", "COU and model-risk definition", "Vendor evidence-request list"),
        recommended_actions_ko=("False-negative 및 calibration 확인", "Borderline scaffold 분석", "독립 human NAM 확보"),
        recommended_actions_en=("Confirm false-negative performance and calibration", "Assess the borderline scaffold", "Obtain independent human NAM evidence"),
        service_tier_ko="진단형 — AI/NAM Evidence Assurance",
        service_tier_en="Diagnostic — AI/NAM Evidence Assurance",
        commercial_model_ko="내부 가격기획 기준: 프로젝트당 $5k–$15k 범주",
        commercial_model_en="Internal pricing reference: project band of $5k–$15k",
        regulatory_anchors=("FDA-AI-2025-DRAFT", "ICH-M15-2026"),
        assessment_builder=_ai_vendor_validation_case,
        expected_role_min=2,
        expected_role_max=2,
    ),
    "CAND-003": ConsultingCase(
        case_id="CAND-003",
        title_ko="대학 Spin-out — 후보물질 3종 독성개발 우선순위",
        title_en="University spin-out — Toxicology-based prioritization of three leads",
        customer_segment_ko="대학 Spin-out·플랫폼 회사",
        customer_segment_en="University spin-out / platform company",
        primary_objective_ko="후보 비교와 투자대상 1개 선정",
        primary_objective_en="Compare candidates and select one for investment",
        engagement_type_ko="Candidate Selection Decision Workshop",
        engagement_type_en="Candidate Selection Decision Workshop",
        trigger_ko="약효 차이는 작지만 독성개발 위험과 필요한 후속비용은 크게 다름",
        trigger_en="Efficacy is similar across leads, but toxicology risk and follow-up cost differ materially",
        decision_question_ko="어떤 후보가 가장 방어 가능한 다음 개발단계를 갖는가?",
        decision_question_en="Which candidate has the most defensible next development step?",
        development_concern_ko="낮음–중간 — 선택된 Lead-B의 근거는 강하나 위원회 검토 전",
        development_concern_en="Low to moderate — Lead-B has strong evidence but awaits committee review",
        automation_scope_ko="개별 후보는 자동평가; 다후보 순위는 Advisor 비교표로 제공",
        automation_scope_en="Each lead is engine-assessed; cross-candidate ranking is advisor-generated",
        deliverables_ko=("후보별 Coverage/Confidence/Concern 매트릭스", "No-regret 추가시험", "후보선정 의사결정 메모"),
        deliverables_en=("Coverage/Confidence/Concern matrix", "No-regret follow-up tests", "Candidate-selection decision memo"),
        recommended_actions_ko=("Lead-B 우선", "Lead-A는 metabolite bridge", "Lead-C는 conflict resolution 후 재평가"),
        recommended_actions_en=("Prioritize Lead-B", "Build a metabolite bridge for Lead-A", "Reassess Lead-C after conflict resolution"),
        service_tier_ko="의사결정형 — 후보·포트폴리오 비교",
        service_tier_en="Decision advisory — Candidate / portfolio comparison",
        commercial_model_ko="내부 가격기획 기준: 프로젝트당 $5k–$15k 범주",
        commercial_model_en="Internal pricing reference: project band of $5k–$15k",
        regulatory_anchors=("FDA-AI-2025-DRAFT", "FDA-NAM-2026-DRAFT", "ICH-M15-2026"),
        assessment_builder=_candidate_comparison_case,
        expected_role_min=3,
        expected_role_max=3,
        related_case_ids=("AI-002", "DD-008"),
    ),
    "RED-004": ConsultingCase(
        case_id="RED-004",
        title_ko="Virtual Biotech — 반복독성시험 축소 전략",
        title_en="Virtual biotech — Strategy to reduce a repeat-dose toxicity study",
        customer_segment_ko="Virtual Biotech",
        customer_segment_en="Virtual biotech",
        primary_objective_ko="동물 수·용량군·중복 endpoint 축소",
        primary_objective_en="Reduce animal numbers, dose groups, and duplicate endpoints",
        engagement_type_ko="3Rs Evidence Strategy",
        engagement_type_en="3Rs Evidence Strategy",
        trigger_ko="CRO 견적은 높고, 사람 관련 AI/NAM·QIVIVE 패키지는 이미 강함",
        trigger_en="The CRO proposal is costly while the human-relevant AI/NAM/QIVIVE package is strong",
        decision_question_ko="어떤 부분을 줄일 수 있고 무엇은 유지해야 하는가?",
        decision_question_en="Which study components can be reduced and which must be retained?",
        development_concern_ko="낮음 — 정의된 간독성 endpoint 내에서만",
        development_concern_en="Low — only within the defined hepatotoxicity endpoint",
        automation_scope_ko="EarlyTox 엔진으로 자동평가 가능",
        automation_scope_en="Supported by the EarlyTox engine",
        deliverables_ko=("3Rs 근거표", "유지·축소·대체후보 endpoint 목록", "CRO 재협상용 설계 메모"),
        deliverables_en=("3Rs evidence table", "Retain/reduce/replacement-candidate endpoint list", "Design memo for CRO renegotiation"),
        recommended_actions_ko=("중복 sampling 축소", "기전·노출 핵심 endpoint 유지", "Agency discussion 전 expert sign-off"),
        recommended_actions_en=("Reduce duplicate sampling", "Retain mechanistic and exposure-critical endpoints", "Expert sign-off before agency discussion"),
        service_tier_ko="전략형 — 규제·시험전략 자문",
        service_tier_en="Strategy — Regulatory and study-planning advisory",
        commercial_model_ko="내부 가격기획 기준: 월 $3k–$8k 또는 프로젝트형",
        commercial_model_en="Internal pricing reference: $3k–$8k/month or project-based",
        regulatory_anchors=("FDA-NAM-2026-DRAFT", "OECD-GIVIMP-2025", "ICH-M15-2026"),
        assessment_builder=_animal_reduction_case,
        expected_role_min=4,
        expected_role_max=4,
    ),
    "GT-005": ConsultingCase(
        case_id="GT-005",
        title_ko="희귀질환 유전자치료제 — 양성 사람 NAM 신호 해석",
        title_en="Rare-disease gene therapy — Interpreting a positive human NAM signal",
        customer_segment_ko="유전자치료 바이오텍",
        customer_segment_en="Gene-therapy biotech",
        primary_objective_ko="양성 신호의 개발영향과 targeted in vivo 범위 결정",
        primary_objective_en="Determine the development impact and targeted in vivo response to a positive signal",
        engagement_type_ko="Positive Signal Escalation Review",
        engagement_type_en="Positive Signal Escalation Review",
        trigger_ko="Human liver organoid에서 양성 신호가 나타났지만 biodistribution과 기존 in vivo 자료도 존재",
        trigger_en="A human liver organoid is positive while biodistribution and prior in vivo data are also available",
        decision_question_ko="근거가 믿을 만한가, 그리고 개발중단이 아니라 어떤 추가확인이 필요한가?",
        decision_question_en="Is the signal credible, and what targeted follow-up is needed short of an automatic stop?",
        development_concern_ko="높음 — 근거 신뢰도와 개발우려를 분리해 관리해야 함",
        development_concern_en="High — evidence credibility must be separated from development concern",
        automation_scope_ko="간독성 Evidence Role은 자동평가; 전체 유전자치료 위험은 전문가 주도",
        automation_scope_en="Hepatotoxicity Evidence Role is engine-supported; full gene-therapy risk remains expert-led",
        deliverables_ko=("양성신호 원인분석", "Biodistribution–NAM–in vivo concordance map", "Targeted follow-up 및 pre-IND 질문"),
        deliverables_en=("Positive-signal root-cause assessment", "Biodistribution–NAM–in vivo concordance map", "Targeted follow-up and pre-IND questions"),
        recommended_actions_ko=("용량·시간 의존성 재확인", "Capsid/active contribution 분리", "간 모니터링·중단기준 초안"),
        recommended_actions_en=("Confirm dose/time dependence", "Separate capsid and active contributions", "Draft liver monitoring and stopping criteria"),
        service_tier_ko="고위험 자문 — 전문가 Escalation",
        service_tier_en="High-impact advisory — Expert escalation",
        commercial_model_ko="내부 가격기획 기준: 월 $3k–$8k 전략자문",
        commercial_model_en="Internal pricing reference: $3k–$8k/month strategy advisory",
        regulatory_anchors=("ICH-S12", "FDA-GENE-EDITING-2026-DRAFT", "FDA-FORMAL-MEETINGS-2026"),
        assessment_builder=_gene_therapy_positive_case,
        expected_role_min=3,
        expected_role_max=3,
    ),
    "MAB-006": ConsultingCase(
        case_id="MAB-006",
        title_ko="항암 mAb — 장기 NHP 시험 간소화 검토",
        title_en="Oncology mAb — Review of a streamlined long-term NHP strategy",
        customer_segment_ko="항암 바이오텍·중견 제약",
        customer_segment_en="Oncology biotech / mid-size pharma",
        primary_objective_ko="불필요한 장기 동물시험 범위 제한",
        primary_objective_en="Limit unnecessary long-term animal-study scope",
        engagement_type_ko="Biologics Streamlining Advisory",
        engagement_type_en="Biologics Streamlining Advisory",
        trigger_ko="단일 표적 mAb의 human-relevant pharmacology와 반복노출 자료가 충분함",
        trigger_en="A monospecific mAb has strong human-relevant pharmacology and repeated-exposure evidence",
        decision_question_ko="어떤 장기 endpoint 또는 반복 NHP 구성요소를 줄일 수 있는가?",
        decision_question_en="Which long-term endpoints or repeat NHP components can be reduced?",
        development_concern_ko="낮음–중간 — 기전·노출 조건 아래 제한적 축소 가능",
        development_concern_en="Low to moderate — limited reduction may be defensible under mechanistic and exposure conditions",
        automation_scope_ko="간독성 slice는 자동평가; 전체 mAb 패키지는 전문가 주도",
        automation_scope_en="Hepatotoxicity slice is engine-supported; the full mAb package remains expert-led",
        deliverables_ko=("장기시험 필요성 논리", "유지 endpoint와 축소 endpoint", "규제기관 논의용 근거표"),
        deliverables_en=("Long-term-study necessity rationale", "Retained vs reduced endpoints", "Evidence table for agency discussion"),
        recommended_actions_ko=("표적조직·면역 안전성은 유지", "중복 장기 간 endpoint 축소 검토", "초안 가이던스 상태 명시"),
        recommended_actions_en=("Retain target-organ and immune-safety monitoring", "Consider reducing duplicate long-term liver endpoints", "State draft-guidance status explicitly"),
        service_tier_ko="전략형 — 동물시험 간소화",
        service_tier_en="Strategy — Nonclinical streamlining",
        commercial_model_ko="내부 가격기획 기준: 월 $3k–$8k 또는 프로젝트형",
        commercial_model_en="Internal pricing reference: $3k–$8k/month or project-based",
        regulatory_anchors=("FDA-MAB-STREAMLINED-2025-DRAFT", "FDA-ONCOLOGY-STREAMLINED-2026-DRAFT"),
        assessment_builder=_mab_streamlining_case,
        expected_role_min=4,
        expected_role_max=4,
    ),
    "CRO-007": ConsultingCase(
        case_id="CRO-007",
        title_ko="CRO 의뢰 전 — 반복독성 프로토콜 독립 검토",
        title_en="Before CRO award — Independent repeat-dose protocol review",
        customer_segment_ko="바이오텍 Sponsor·CRO",
        customer_segment_en="Biotech sponsor / CRO",
        primary_objective_ko="비용 집행 전 시험목적·설계 적절성 확인",
        primary_objective_en="Confirm purpose and design adequacy before committing spend",
        engagement_type_ko="Protocol Readiness Review",
        engagement_type_en="Protocol Readiness Review",
        trigger_ko="CRO 초안에 대조군, 반복노출 bridge, 실제 노출 및 재현성 근거가 부족",
        trigger_en="The CRO draft lacks adequate controls, repeated-exposure bridging, measured exposure, and reproducibility",
        decision_question_ko="이 프로토콜로 표적장기·노출반응·회복성 질문에 답할 수 있는가?",
        decision_question_en="Can this protocol answer target-organ, exposure-response, and recovery questions?",
        development_concern_ko="미정 — 현재 설계로는 음성결과도 신뢰하기 어려움",
        development_concern_en="Unknown — a negative result would be difficult to trust under the current design",
        automation_scope_ko="EarlyTox 엔진으로 사전 설계 gap 자동평가 가능",
        automation_scope_en="Pre-study design gaps are supported by the EarlyTox engine",
        deliverables_ko=("프로토콜 Redline", "필수·선택 endpoint 매트릭스", "CRO 질의서"),
        deliverables_en=("Protocol redline", "Required vs optional endpoint matrix", "CRO clarification questions"),
        recommended_actions_ko=("유효한 positive control", "반복노출 NAM/bridge", "TK·회복성·실제 노출 설계"),
        recommended_actions_en=("Add a valid positive control", "Add repeated-exposure NAM/bridge", "Integrate TK, recovery, and measured exposure"),
        service_tier_ko="진단형 — 시험설계 검토",
        service_tier_en="Diagnostic — Study-design review",
        commercial_model_ko="내부 가격기획 기준: 프로젝트당 $5k–$15k 범주",
        commercial_model_en="Internal pricing reference: project band of $5k–$15k",
        regulatory_anchors=("OECD-GIVIMP-2025", "ICH-M3R2"),
        assessment_builder=_cro_protocol_review_case,
        expected_role_min=2,
        expected_role_max=2,
    ),
    "DD-008": ConsultingCase(
        case_id="DD-008",
        title_ko="중견 제약 — License-in 독성 Data Room 실사",
        title_en="Mid-size pharma — License-in toxicology data-room diligence",
        customer_segment_ko="중견 제약·Business Development",
        customer_segment_en="Mid-size pharma / business development",
        primary_objective_ko="거래 전 숨은 독성·근거 리스크 정량화",
        primary_objective_en="Characterize hidden toxicity and evidence risk before a transaction",
        engagement_type_ko="Nonclinical Due Diligence",
        engagement_type_en="Nonclinical Due Diligence",
        trigger_ko="Seller는 AI 음성결과를 강조하지만 human organoid는 양성",
        trigger_en="The seller emphasizes a negative AI result while a human organoid is positive",
        decision_question_ko="이 상충이 거래가치, milestone, indemnity 및 추가실사에 어떤 영향을 주는가?",
        decision_question_en="How should the conflict affect valuation, milestones, indemnity, and further diligence?",
        development_concern_ko="중간–높음 — 상충 근거가 해소되기 전 거래조건에 반영 필요",
        development_concern_en="Moderate to high — unresolved conflict should affect transaction terms",
        automation_scope_ko="Evidence Role은 자동평가; 거래구조 권고는 전문가 주도",
        automation_scope_en="Evidence Role is engine-supported; transaction structuring is expert-led",
        deliverables_ko=("Red-flag memo", "Data Room gap list", "Deal term에 반영할 조건·milestone"),
        deliverables_en=("Red-flag memo", "Data-room gap list", "Conditions and milestones for deal terms"),
        recommended_actions_ko=("Orthogonal NAM", "원자료·lot·노출 재검토", "조건부 milestone 또는 holdback"),
        recommended_actions_en=("Orthogonal NAM", "Re-review raw data, lots, and exposure", "Conditional milestone or holdback"),
        service_tier_ko="거래형 — 비임상 Due Diligence",
        service_tier_en="Transaction advisory — Nonclinical due diligence",
        commercial_model_ko="내부 가격기획 기준: 프로젝트당 $5k–$15k 이상, 범위별 견적",
        commercial_model_en="Internal pricing reference: $5k–$15k+ depending on scope",
        regulatory_anchors=("FDA-AI-2025-DRAFT", "FDA-NAM-2026-DRAFT"),
        assessment_builder=_license_in_due_diligence_case,
        expected_role_min=2,
        expected_role_max=2,
    ),
    "PREIND-009": ConsultingCase(
        case_id="PREIND-009",
        title_ko="Pre-IND 준비 — 질문 중심 Meeting Package",
        title_en="Pre-IND preparation — Question-driven meeting package",
        customer_segment_ko="임상진입 준비 바이오텍",
        customer_segment_en="Clinical-entry biotech",
        primary_objective_ko="FDA에 확인할 질문과 Evidence Role 경계 설정",
        primary_objective_en="Define agency questions and evidence-role boundaries",
        engagement_type_ko="Pre-IND Question & Briefing Package",
        engagement_type_en="Pre-IND Question & Briefing Package",
        trigger_ko="과학근거는 강하지만 AI/NAM을 어느 수준으로 주장할지와 질문구성이 불명확",
        trigger_en="The science is strong, but the claim level and agency questions are unclear",
        decision_question_ko="AI/NAM 근거를 screening, supportive, reduction-support 중 어디까지 제시할 것인가?",
        decision_question_en="Should the AI/NAM evidence be positioned as screening, supportive, or reduction-supporting?",
        development_concern_ko="낮음 — 핵심은 안전결론이 아니라 규제 주장범위와 질문설계",
        development_concern_en="Low — the key issue is claim scope and question design, not a safety conclusion",
        automation_scope_ko="Evidence Role 자동평가 + 전문가 meeting strategy",
        automation_scope_en="Engine-supported Evidence Role plus expert meeting strategy",
        deliverables_ko=("Meeting objective와 agenda", "P/T 질문 5–8개", "Evidence summary와 fallback position"),
        deliverables_en=("Meeting objective and agenda", "Five to eight P/T questions", "Evidence summary and fallback position"),
        recommended_actions_ko=("COU를 좁게 정의", "초안 가이던스 상태 표시", "FDA 답변별 decision tree 준비"),
        recommended_actions_en=("Narrowly define the COU", "Disclose draft-guidance status", "Prepare a decision tree for possible FDA responses"),
        service_tier_ko="규제상호작용형 — Pre-IND 준비",
        service_tier_en="Regulatory interaction — Pre-IND preparation",
        commercial_model_ko="내부 가격기획 기준: CTA/IND 지원 $10k–$30k 범주",
        commercial_model_en="Internal pricing reference: CTA/IND support band of $10k–$30k",
        regulatory_anchors=("FDA-FORMAL-MEETINGS-2026", "FDA-PREIND-FAQ", "FDA-AI-ENGAGEMENT-2026"),
        assessment_builder=_preind_meeting_case,
        expected_role_min=3,
        expected_role_max=3,
    ),
    "COMP-010": ConsultingCase(
        case_id="COMP-010",
        title_ko="제형 변경 — 독성시험 배치와 임상제품 Comparability",
        title_en="Formulation change — Comparability between tox batch and clinical product",
        customer_segment_ko="제약사 CMC·독성 공동팀",
        customer_segment_en="Pharma CMC / toxicology joint team",
        primary_objective_ko="기존 독성근거의 bridging 가능성 판단",
        primary_objective_en="Determine whether existing toxicology evidence can be bridged",
        engagement_type_ko="CMC–Toxicology Comparability Review",
        engagement_type_en="CMC–Toxicology Comparability Review",
        trigger_ko="입자크기·표면조성·free active가 변경됐으나 기존 독성시험 재사용을 희망",
        trigger_en="Particle size, surface composition, and free active changed, but the team wants to reuse the tox study",
        decision_question_ko="어떤 CQA 차이는 bridging 가능하고 어떤 차이는 추가시험을 요구하는가?",
        decision_question_en="Which CQA differences can be bridged and which require additional testing?",
        development_concern_ko="미정 — CQA-독성 연결과 test article 대표성 확인 전 낮게 분류 불가",
        development_concern_en="Unknown — cannot be considered low until CQA–toxicity linkage and representativeness are established",
        automation_scope_ko="간독성 Evidence Role은 자동평가; Comparability 결론은 전문가 주도",
        automation_scope_en="Hepatotoxicity Evidence Role is engine-supported; comparability conclusion is expert-led",
        deliverables_ko=("CQA comparability matrix", "Bridging rationale", "추가 분석·NAM·targeted in vivo 의사결정"),
        deliverables_en=("CQA comparability matrix", "Bridging rationale", "Decision on added analytics, NAM, or targeted in vivo work"),
        recommended_actions_ko=("입자크기·분포·표면전하·free active 비교", "Carrier-only 비교", "임상배치 대표성 formal assessment"),
        recommended_actions_en=("Compare particle size/distribution, surface charge, and free active", "Compare carrier-only effects", "Formal clinical-batch representativeness assessment"),
        service_tier_ko="기술전략형 — CMC/Tox Bridging",
        service_tier_en="Technical strategy — CMC/toxicology bridging",
        commercial_model_ko="내부 가격기획 기준: 월 $3k–$8k 또는 프로젝트형",
        commercial_model_en="Internal pricing reference: $3k–$8k/month or project-based",
        regulatory_anchors=("ICH-M3R2", "FDA-PREIND-FAQ"),
        assessment_builder=_comparability_bridge_case,
        expected_role_min=3,
        expected_role_max=3,
    ),
    "VC-011": ConsultingCase(
        case_id="VC-011",
        title_ko="VC·액셀러레이터 — 포트폴리오 3개 자산 독성 리스크 Triage",
        title_en="VC / accelerator — Toxicology-risk triage across three portfolio assets",
        customer_segment_ko="VC·액셀러레이터",
        customer_segment_en="VC / accelerator",
        primary_objective_ko="실사시간을 줄이고 자금집행 우선순위 설정",
        primary_objective_en="Reduce diligence time and prioritize capital deployment",
        engagement_type_ko="Portfolio Toxicology Triage",
        engagement_type_en="Portfolio Toxicology Triage",
        trigger_ko="서로 다른 modality와 근거성숙도를 가진 3개 회사에 동일한 체크리스트를 적용하기 어려움",
        trigger_en="Three companies have different modalities and evidence maturity, making a single checklist inadequate",
        decision_question_ko="어떤 자산에 추가실사, 조건부 투자 또는 보류가 필요한가?",
        decision_question_en="Which assets require deeper diligence, conditional investment, or a hold?",
        development_concern_ko="혼합 — R4 저위험 자산, R2 상충 자산, R1 적용범위 밖 자산",
        development_concern_en="Mixed — one R4 low-concern asset, one R2 conflicting asset, and one R1 out-of-domain asset",
        automation_scope_ko="개별 자산은 자동평가; 포트폴리오 자본배분은 전문가 주도",
        automation_scope_en="Each asset is engine-assessed; portfolio capital allocation is expert-led",
        deliverables_ko=("3자산 Heatmap", "투자조건·milestone 제안", "90일 실사계획"),
        deliverables_en=("Three-asset heatmap", "Investment conditions and milestones", "90-day diligence plan"),
        recommended_actions_ko=("R4 자산 우선검토", "상충 자산은 orthogonal confirmation", "R1 자산은 최소 패키지 후 재평가"),
        recommended_actions_en=("Prioritize the R4 asset", "Require orthogonal confirmation for the conflicting asset", "Reassess the R1 asset after a minimum evidence package"),
        service_tier_ko="포트폴리오형 — VC Risk Triage",
        service_tier_en="Portfolio advisory — VC risk triage",
        commercial_model_ko="내부 가격기획 기준: 자산 수와 data-room 범위에 따른 프로젝트 견적",
        commercial_model_en="Internal pricing reference: project quote based on asset count and data-room scope",
        regulatory_anchors=("FDA-AI-2025-DRAFT", "FDA-NAM-2026-DRAFT"),
        assessment_builder=None,
        related_case_ids=("LAB-001", "RED-004", "DD-008"),
    ),
    "IMP-012": ConsultingCase(
        case_id="IMP-012",
        title_ko="허가·품질팀 — NDSRI/니트로사민 안전성 Qualification",
        title_en="Regulatory / quality team — NDSRI and nitrosamine safety qualification",
        customer_segment_ko="허가품목 보유 제약사",
        customer_segment_en="Pharma company with marketed products",
        primary_objective_ko="불순물 위험, 허용섭취량 및 보완시험 전략 결정",
        primary_objective_en="Determine impurity risk, acceptable intake, and follow-up testing strategy",
        engagement_type_ko="Impurity Safety & Regulatory Response",
        engagement_type_en="Impurity Safety & Regulatory Response",
        trigger_ko="NDSRI가 검출됐으나 구조유사성, QSAR, 노출 및 관리전략이 분산돼 있음",
        trigger_en="An NDSRI was detected, but structural analog, QSAR, exposure, and control evidence are fragmented",
        decision_question_ko="어떤 근거가 현재 limit를 방어하고 어떤 추가시험·규제보고가 필요한가?",
        decision_question_en="What supports the current limit, and what testing or regulatory response is still required?",
        development_concern_ko="중간–높음 — 노출과 potency 분류가 확정될 때까지 품질·환자안전 리스크 존재",
        development_concern_en="Moderate to high — quality and patient-safety risk remains until exposure and potency categorization are resolved",
        automation_scope_ko="현재 EarlyTox 자동화 범위 밖; 전문가 주도 자문",
        automation_scope_en="Outside the current EarlyTox automation scope; expert-led advisory",
        deliverables_ko=("NDSRI risk dossier", "QSAR·analogue·exposure weight-of-evidence", "Limit·CAPA·규제보고 로드맵"),
        deliverables_en=("NDSRI risk dossier", "QSAR/analogue/exposure weight of evidence", "Limit, CAPA, and regulatory-reporting roadmap"),
        recommended_actions_ko=("공식 구조·분석법·일일노출 확정", "2개 보완 QSAR와 analogue 검토", "공정·원료·안정성 원인분석"),
        recommended_actions_en=("Confirm structure, method, and daily exposure", "Use two complementary QSAR systems and analogue review", "Investigate process, raw-material, and stability sources"),
        service_tier_ko="고위험 자문 — 불순물·규제 대응",
        service_tier_en="High-impact advisory — Impurity and regulatory response",
        commercial_model_ko="내부 가격기획 기준: CTA/IND·규제문서 지원 $10k–$30k 범주 또는 범위별 견적",
        commercial_model_en="Internal pricing reference: $10k–$30k regulatory-support band or scope-based quote",
        regulatory_anchors=("FDA-NITROSAMINE-2024", "ICH-M7R2"),
        assessment_builder=None,
    ),
    "TAC-101": ConsultingCase(
        case_id="TAC-101",
        title_ko="Tacrolimus 제형·제네릭 — trough가 같아도 peak 독성위험을 놓치는가?",
        title_en="Tacrolimus formulation/generic — Can similar troughs conceal peak-related toxicity risk?",
        customer_segment_ko="제네릭 개발사·License-in 팀·병원 약사위원회",
        customer_segment_en="Generic sponsor / license-in team / hospital formulary committee",
        primary_objective_ko="NTI 제품의 therapeutic equivalence와 전환위험 검토",
        primary_objective_en="Review therapeutic equivalence and switching risk for an NTI product",
        engagement_type_ko="NTI Bioequivalence & Formulation Risk Review",
        engagement_type_en="NTI Bioequivalence & Formulation Risk Review",
        trigger_ko="Trough와 총 노출은 유사해 보이지만 Cmax 차이 또는 제형변경이 독성위험을 바꿀 가능성이 있음",
        trigger_en="Trough and overall exposure appear similar, but Cmax or formulation differences may alter toxicity risk",
        decision_question_ko="Tacrolimus에서 trough 또는 AUC 유사성만으로 자동대체와 임상 전환을 방어할 수 있는가?",
        decision_question_en="For tacrolimus, are similar troughs or AUC sufficient to support automatic substitution and clinical switching?",
        development_concern_ko="높음 — 좁은 치료지수에서 peak 상승은 신독성·신경독성·고칼륨혈증 등 과노출 위험을 높일 수 있으나, 특정 제품의 실제 임상 위해는 별도 자료로 판단해야 함",
        development_concern_en="High — with a narrow therapeutic index, higher peaks may increase overexposure risks such as nephrotoxicity, neurotoxicity, and hyperkalemia, while actual clinical harm for a specific product requires separate evidence",
        automation_scope_ko="현재 EarlyTox 자동화 범위 밖; 임상약리·제형·BE 전문가 주도",
        automation_scope_en="Outside the current EarlyTox automation scope; expert-led clinical pharmacology, formulation, and BE review",
        deliverables_ko=("Cmax·AUC·trough·partial-AUC 비교표", "제형·용출·식이·상호작용 위험지도", "제품전환 TDM 및 임상 모니터링 계획", "Therapeutic-equivalence 주장 경계 메모"),
        deliverables_en=("Cmax/AUC/trough/partial-AUC comparison", "Formulation, dissolution, food, and interaction risk map", "Switching TDM and clinical-monitoring plan", "Therapeutic-equivalence claim-boundary memo"),
        recommended_actions_ko=("평균 BE뿐 아니라 peak와 개인내 변동성을 검토", "제품별 방출·흡수 차이와 Cmax 민감도를 분석", "전환 전후 trough·신기능·신경학적 증상·전해질 모니터링 설계", "자동대체 가능성과 승인상태를 분리해 설명"),
        recommended_actions_en=("Review peak exposure and within-subject variability, not only average BE", "Assess product-specific release/absorption and Cmax sensitivity", "Design pre/post-switch monitoring of trough, renal function, neurologic findings, and electrolytes", "Separate approval status from automatic substitutability"),
        service_tier_ko="고위험 자문 — NTI 제형·BE·전환전략",
        service_tier_en="High-impact advisory — NTI formulation, BE, and switching strategy",
        commercial_model_ko="범위별 프로젝트 — PK 원자료·제형·규제상태에 따라 견적",
        commercial_model_en="Scope-based project — quoted according to PK source data, formulation, and regulatory status",
        regulatory_anchors=("TACROLIMUS-LABEL-CURRENT", "FDA-TAC-TE-2023", "FDA-TE-GUIDANCE-2026", "EMA-TAC-BE-2026"),
        assessment_builder=None,
        related_case_ids=("TAC-102", "TAC-103"),
        asset_ko="Tacrolimus",
        asset_en="Tacrolimus",
        case_basis_ko="공식 라벨·FDA therapeutic-equivalence 조치·EMA BE 가이던스에 기반한 회고적 벤치마크와 합성 고객상황",
        case_basis_en="Retrospective benchmark based on the official label, FDA therapeutic-equivalence action, and EMA BE guidance, combined with a synthetic client scenario",
        public_evidence_ko=("Tacrolimus 라벨은 신독성, 신경독성, 고칼륨혈증, 고혈압 및 CYP3A 상호작용을 주요 위험으로 다룸", "FDA는 2023년 특정 제품(Accord)에서 Prograf 대비 높은 peak 가능성을 근거로 TE 등급을 AB에서 BX로 변경했으며 trough 차이는 유의하지 않았다고 설명", "EMA의 tacrolimus granules 제품별 BE 가이던스는 Cmax와 AUC 지표를 명시"),
        public_evidence_en=("The tacrolimus label addresses nephrotoxicity, neurotoxicity, hyperkalemia, hypertension, and CYP3A interactions", "In 2023 FDA changed the TE rating for specific Accord capsules from AB to BX based on a possible higher peak than Prograf while noting no significant trough difference", "EMA product-specific BE guidance for tacrolimus granules explicitly addresses Cmax and AUC metrics"),
        synthetic_assumptions_ko=("고객은 새로운 제네릭 또는 license-in 제품의 PK/BE 자료를 검토 중", "전환 대상 환자는 tacrolimus 치료가 안정화된 이식환자", "제품별 원자료와 제형 비교가 가능하다고 가정"),
        synthetic_assumptions_en=("The client is reviewing PK/BE evidence for a new generic or license-in product", "The intended switch population consists of stable transplant recipients", "Product-level source data and formulation comparisons are assumed available"),
        advisory_inferences_ko=("Trough 일치만으로 peak 관련 독성위험이 배제되지 않음", "승인 여부와 자동대체 가능성은 동일한 질문이 아님", "NORA는 BE 판정을 대신하기보다 peak–trough–임상 모니터링의 근거연결을 검토"),
        advisory_inferences_en=("Trough agreement alone does not exclude peak-related toxicity risk", "Regulatory approval and automatic substitutability are not the same question", "NORA reviews the evidence chain linking peak, trough, and clinical monitoring rather than replacing formal BE assessment"),
    ),
    "TAC-102": ConsultingCase(
        case_id="TAC-102",
        title_ko="Tacrolimus AI/PopPK 용량추천 — CYP3A5와 azole 병용에서 모델을 믿을 수 있는가?",
        title_en="Tacrolimus AI/PopPK dosing — Is the model reliable with CYP3A5 and azole co-therapy?",
        customer_segment_ko="이식센터·디지털헬스·임상약리 AI 기업",
        customer_segment_en="Transplant center / digital-health company / clinical-pharmacology AI vendor",
        primary_objective_ko="초기 용량추천 모델의 실제 진료 적용성과 실패위험 검증",
        primary_objective_en="Validate real-world applicability and failure risk of an initial-dose model",
        engagement_type_ko="AI Dosing Model Credibility & Deployment Review",
        engagement_type_en="AI Dosing Model Credibility & Deployment Review",
        trigger_ko="CYP3A5 유전자형과 azole 상호작용을 결합한 모델을 조기 이식환자에 배포하려 하지만 외부 타당성이 불명확",
        trigger_en="A model combining CYP3A5 genotype and azole interactions is proposed for early transplant care, but external validity is uncertain",
        decision_question_ko="이 모델을 시작용량 추천에 사용할 수 있는가, 아니면 silent-mode 및 TDM 보조로 제한해야 하는가?",
        decision_question_en="Can this model recommend starting doses, or should it remain in silent mode and support TDM only?",
        development_concern_ko="높음 — 과대 또는 과소 예측은 독성 또는 거부반응 위험으로 이어질 수 있으며 장기·이식장기·시점·병용약·검사법이 성능을 크게 바꿀 수 있음",
        development_concern_en="High — over- or underprediction can contribute to toxicity or rejection, and performance may vary by organ, post-transplant time, co-medications, and assay",
        automation_scope_ko="AI Credibility 프레임은 적용 가능하나 실제 투약권고는 임상전문가·약사 주도",
        automation_scope_en="The AI credibility framework applies, but actual dosing recommendations remain clinician- and pharmacist-led",
        deliverables_ko=("Model Card·COU·Model Risk 평가", "기관·이식장기·시점·유전자형별 외부검증 계획", "Silent-mode prospective validation protocol", "Clinician override·TDM·drift monitoring 설계"),
        deliverables_en=("Model Card, COU, and Model Risk assessment", "External-validation plan by center, organ, time, and genotype", "Silent-mode prospective validation protocol", "Clinician override, TDM, and drift-monitoring design"),
        recommended_actions_ko=("CYP3A5 외 CYP3A4 억제제·간기능·설사·hematocrit·이식 후 시점을 포함", "기관 자료에서 calibration과 ±30% dose accuracy를 재검증", "처방 전 silent-mode로 prospective 성능 확인", "모델 출력보다 TDM과 임상 상태를 최종 조정기준으로 유지"),
        recommended_actions_en=("Include CYP3A4 inhibitors, liver function, diarrhea, hematocrit, and time after transplant in addition to CYP3A5", "Revalidate calibration and ±30% dose accuracy in local data", "Run prospectively in silent mode before influencing prescriptions", "Keep TDM and clinical status as the final adjustment basis"),
        service_tier_ko="AI 자문 — 임상용량 모델 검증·배포 거버넌스",
        service_tier_en="AI advisory — Clinical dosing-model validation and deployment governance",
        commercial_model_ko="단계형 프로젝트 — retrospective validation → silent pilot → monitored deployment",
        commercial_model_en="Phased engagement — retrospective validation → silent pilot → monitored deployment",
        regulatory_anchors=("CPIC-TAC-CYP3A5-2015", "TACROLIMUS-LABEL-CURRENT", "TAC-AZOLE-VALIDATION-2025", "FDA-AI-2025-DRAFT", "ICH-M15-2026"),
        assessment_builder=None,
        related_case_ids=("TAC-101", "TAC-103"),
        asset_ko="Tacrolimus",
        asset_en="Tacrolimus",
        case_basis_ko="CPIC 지침과 2025년 azole 병용 폐이식 환자 외부성능 연구에 기반한 합성 AI 배포 사례",
        case_basis_en="Synthetic AI deployment case grounded in CPIC guidance and a 2025 external-performance study in lung-transplant recipients receiving azoles",
        public_evidence_ko=("CPIC은 CYP3A5 expresser에서 표준 시작용량의 1.5–2배를 고려하되 0.3 mg/kg/day를 넘지 않고 TDM으로 조정하도록 권고", "2025년 azole 병용 폐이식 환자 연구에서는 CYP3A5·azole 조정용량의 예측정확도가 시점에 따라 낮아져 맥락별 외부검증 필요성을 보여줌", "Tacrolimus는 좁은 치료지수와 다수 상호작용 때문에 지속적인 TDM이 중요"),
        public_evidence_en=("CPIC recommends considering 1.5–2 times the standard starting dose for CYP3A5 expressers, not exceeding 0.3 mg/kg/day, with TDM-guided adjustment", "A 2025 study in azole-treated lung-transplant recipients found declining accuracy of CYP3A5/azole-adjusted dosing over time, illustrating the need for contextual external validation", "Tacrolimus has a narrow therapeutic index and multiple interactions, making ongoing TDM important"),
        synthetic_assumptions_ko=("고객 모델은 유전자형·체중·azole 종류를 입력으로 사용", "기관별 검사법과 이식 후 시점 분포가 학습자료와 다름", "초기에는 처방을 바꾸지 않는 silent deployment가 가능"),
        synthetic_assumptions_en=("The client model uses genotype, weight, and azole type as inputs", "Local assay methods and post-transplant timing differ from the training data", "A silent deployment that does not alter prescribing is feasible initially"),
        advisory_inferences_ko=("가이드라인 규칙을 모델에 넣었다고 해서 현장 성능이 보장되지 않음", "평균 오차보다 독성·거부반응으로 이어질 극단 오차와 subgroup calibration이 중요", "모델은 TDM을 대체하지 않고 초기정보와 모니터링 우선순위를 보조해야 함"),
        advisory_inferences_en=("Encoding guideline rules does not guarantee performance in the deployment setting", "Extreme errors and subgroup calibration matter more than average error when toxicity or rejection can result", "The model should support initial information and monitoring priorities rather than replace TDM"),
    ),
    "TAC-103": ConsultingCase(
        case_id="TAC-103",
        title_ko="Tacrolimus 검사법 전환 — assay bias가 용량 알고리즘을 왜곡하는가?",
        title_en="Tacrolimus assay transition — Can assay bias distort dosing algorithms?",
        customer_segment_ko="임상검사실·이식 네트워크·병원 데이터팀",
        customer_segment_en="Clinical laboratory / transplant network / hospital data team",
        primary_objective_ko="면역측정법·LC-MS/MS 전환 시 과거 목표범위와 모델의 연속성 검증",
        primary_objective_en="Validate continuity of historical targets and models during immunoassay/LC-MS/MS transition",
        engagement_type_ko="Assay Comparability & Clinical Algorithm Recalibration",
        engagement_type_en="Assay Comparability & Clinical Algorithm Recalibration",
        trigger_ko="Tacrolimus 측정 플랫폼을 변경하면서 과거 therapeutic range와 AI/PopPK 모델을 그대로 사용하려 함",
        trigger_en="The tacrolimus measurement platform is changing while historical therapeutic ranges and AI/PopPK models are expected to remain unchanged",
        decision_question_ko="새 assay 결과를 기존 목표범위와 용량조정 알고리즘에 그대로 연결할 수 있는가?",
        decision_question_en="Can results from the new assay be used directly with existing target ranges and dose-adjustment algorithms?",
        development_concern_ko="중간–높음 — parent drug와 대사체 교차반응 또는 matrix 간섭에 따른 체계적 bias가 잘못된 용량조정으로 이어질 수 있음",
        development_concern_en="Moderate to high — systematic bias from parent/metabolite cross-reactivity or matrix interference can drive incorrect dose adjustments",
        automation_scope_ko="현재 EarlyTox 범위 밖; 분석법·통계·임상약리 전문가 주도",
        automation_scope_en="Outside the current EarlyTox scope; expert-led analytical, statistical, and clinical-pharmacology review",
        deliverables_ko=("Paired-sample method-comparison 분석계획", "Decision-level bias·commutability·cross-reactivity 매트릭스", "Therapeutic range 및 AI 모델 재보정 전략", "검사법 변경 임상 커뮤니케이션 계획"),
        deliverables_en=("Paired-sample method-comparison analysis plan", "Decision-level bias, commutability, and cross-reactivity matrix", "Therapeutic-range and AI-model recalibration strategy", "Clinical communication plan for assay transition"),
        recommended_actions_ko=("의사결정 농도대에서 paired specimen 비교", "Deming/Passing–Bablok·Bland–Altman과 임상분류 일치도를 함께 평가", "MI–MVIII 대사체 교차반응과 hematocrit·bilirubin·lipid 간섭 확인", "새 assay로 모델과 target range를 재검증 후 단계 전환"),
        recommended_actions_en=("Compare paired specimens near clinical decision concentrations", "Use Deming/Passing–Bablok, Bland–Altman, and clinical classification agreement", "Assess MI–MVIII metabolite cross-reactivity and hematocrit, bilirubin, and lipid interference", "Revalidate models and target ranges under the new assay before phased transition"),
        service_tier_ko="방법·데이터 자문 — Assay bridging과 알고리즘 재보정",
        service_tier_en="Method/data advisory — Assay bridging and algorithm recalibration",
        commercial_model_ko="범위별 프로젝트 — 검체수·플랫폼수·모델 재검증 범위에 따라 견적",
        commercial_model_en="Scope-based project — quoted according to sample count, platforms, and model-revalidation scope",
        regulatory_anchors=("FDA-TAC-ASSAY-SPECIAL-CONTROLS", "TACROLIMUS-LABEL-CURRENT", "ICH-M15-2026"),
        assessment_builder=None,
        related_case_ids=("TAC-101", "TAC-102"),
        asset_ko="Tacrolimus",
        asset_en="Tacrolimus",
        case_basis_ko="FDA tacrolimus assay special controls와 TDM 맥락을 이용한 합성 검사실 전환 사례",
        case_basis_en="Synthetic laboratory-transition case using FDA tacrolimus assay special controls and the TDM context",
        public_evidence_ko=("FDA special controls는 tacrolimus assay specificity 평가에서 MI–MVIII 대사체 교차반응을 특성화하도록 권고", "간섭물질, 검체 matrix, 반복측정, 대사체 순도와 계산방식을 문서화해야 함", "Tacrolimus 의사결정은 측정값의 작은 체계적 차이에 민감할 수 있음"),
        public_evidence_en=("FDA special controls recommend characterizing cross-reactivity with tacrolimus metabolites MI–MVIII", "Interferents, sample matrix, replicates, metabolite purity, and computation methods should be documented", "Tacrolimus decisions can be sensitive to small systematic measurement differences"),
        synthetic_assumptions_ko=("고객은 immunoassay에서 LC-MS/MS 또는 다른 플랫폼으로 전환", "기존 target range와 모델은 이전 assay 자료로 개발", "paired residual specimens와 임상결정 이력이 제공됨"),
        synthetic_assumptions_en=("The client is transitioning from an immunoassay to LC-MS/MS or another platform", "Existing target ranges and models were developed with the prior assay", "Paired residual specimens and clinical-decision histories are available"),
        advisory_inferences_ko=("상관계수가 높아도 임상결정 농도대의 bias가 허용된다는 뜻은 아님", "검사법 변경은 데이터 drift이자 모델 input-definition 변경", "모델과 치료범위를 새 assay에 맞춰 재검증해야 함"),
        advisory_inferences_en=("High correlation does not establish acceptable bias at clinical decision levels", "An assay change is both data drift and a change in model input definition", "Models and therapeutic ranges require revalidation for the new assay"),
    ),
    "TIR-201": ConsultingCase(
        case_id="TIR-201",
        title_ko="Tirzepatide 설치류 C-cell 종양 — 사람 관련성을 어떻게 판단할 것인가?",
        title_en="Tirzepatide rodent C-cell tumors — How should human relevance be assessed?",
        customer_segment_ko="차세대 incretin 개발사·독성팀·규제전략팀",
        customer_segment_en="Next-generation incretin sponsor / toxicology team / regulatory strategy team",
        primary_objective_ko="설치류 발암성 신호의 사람 번역성과 후보별 추가근거 설계",
        primary_objective_en="Assess human translation of a rodent carcinogenicity signal and design candidate-specific evidence",
        engagement_type_ko="Species Relevance & Mechanistic Risk Translation",
        engagement_type_en="Species Relevance & Mechanistic Risk Translation",
        trigger_ko="Tirzepatide 라벨의 rat thyroid C-cell 종양 신호를 신규 dual/triple agonist의 class risk로 해석하려 함",
        trigger_en="The tirzepatide label's rat thyroid C-cell tumor signal is being used to infer class risk for a new dual/triple agonist",
        decision_question_ko="Rat 종양신호를 사람 위험 또는 신규 후보의 위험으로 어느 범위까지 외삽할 수 있는가?",
        decision_question_en="How far can the rat tumor signal be extrapolated to human risk or a new candidate?",
        development_concern_ko="중대하지만 사람 관련성 미정 — 공식 라벨은 설치류 소견을 인정하나 사람에서의 관련성은 확정되지 않았다고 명시",
        development_concern_en="Serious but human relevance unresolved — the official label recognizes the rodent finding while stating that its relevance to humans has not been determined",
        automation_scope_ko="현재 간독성 자동화 범위 밖; 발암성·비교생물학·임상약리 전문가 주도",
        automation_scope_en="Outside the current hepatotoxicity automation scope; expert-led carcinogenicity, comparative-biology, and clinical-pharmacology review",
        deliverables_ko=("Rat–mouse–human C-cell biology 비교표", "Receptor expression·활성·노출·기전 Weight of Evidence", "신규 후보 class-to-candidate gap 분석", "규제기관 질문 및 주장 경계"),
        deliverables_en=("Rat–mouse–human C-cell biology comparison", "Receptor expression, activation, exposure, and mechanistic weight of evidence", "Class-to-candidate gap analysis", "Agency questions and claim boundaries"),
        recommended_actions_ko=("Rat 소견의 용량·기간·AUC 정합성 검토", "Human thyroid C-cell의 receptor expression과 기능자료 평가", "rasH2 음성·micronucleus 음성을 각각 발암성·유전독성 맥락에서 해석", "신규 후보의 receptor balance와 chronic exposure를 별도 검증"),
        recommended_actions_en=("Review dose, duration, and AUC context of the rat findings", "Evaluate receptor expression and function in human thyroid C cells", "Interpret the negative rasH2 and micronucleus results within their specific carcinogenicity and genotoxicity contexts", "Validate receptor balance and chronic exposure for the new candidate separately"),
        service_tier_ko="고위험 자문 — 발암성 신호의 사람 관련성",
        service_tier_en="High-impact advisory — Human relevance of a carcinogenicity signal",
        commercial_model_ko="전문가 프로젝트 — 공개자료 리뷰 + 후보별 비공개 근거 검토",
        commercial_model_en="Expert project — public-evidence review plus candidate-specific confidential evidence",
        regulatory_anchors=("MOUNJARO-LABEL-2026", "TIRZEPATIDE-MECHANISM-2020"),
        assessment_builder=None,
        related_case_ids=("TIR-202", "TIR-203"),
        asset_ko="Tirzepatide",
        asset_en="Tirzepatide",
        case_basis_ko="현행 Mounjaro 라벨의 비임상 소견을 신규 incretin 후보의 benchmark로 사용하는 합성 개발 사례",
        case_basis_en="Synthetic development case using the current Mounjaro label's nonclinical findings as a benchmark for a new incretin candidate",
        public_evidence_ko=("현행 라벨은 2년 rat 시험에서 임상 관련 노출의 dose·duration-dependent thyroid C-cell 종양 증가를 기술", "사람에서의 관련성은 결정되지 않았다고 명시", "6개월 rasH2 mouse 시험은 종양원성 음성이었고 rat micronucleus 시험은 유전독성 음성이었음"),
        public_evidence_en=("The current label describes dose- and duration-dependent thyroid C-cell tumors in a two-year rat study at clinically relevant exposures", "The label states that human relevance has not been determined", "A six-month rasH2 mouse study was not tumorigenic and a rat micronucleus assay was negative for genotoxicity"),
        synthetic_assumptions_ko=("고객은 tirzepatide와 다른 receptor balance를 가진 신규 dual/triple agonist를 개발", "신규 후보의 장기 노출 및 thyroid 관련 자료는 아직 제한적", "공개 tirzepatide 자료를 class benchmark로 사용하려 함"),
        synthetic_assumptions_en=("The client is developing a new dual/triple agonist with a receptor balance different from tirzepatide", "Long-term exposure and thyroid-related data for the new candidate remain limited", "Public tirzepatide evidence is being considered as a class benchmark"),
        advisory_inferences_ko=("Rat 소견을 사람 인과위험으로 확정하거나 무관하다고 단정할 수 없음", "rasH2 및 micronucleus 음성은 rat C-cell 소견을 자동으로 무효화하지 않음", "Class benchmark는 질문을 정의하지만 후보별 chronic tox와 기전자료를 대체하지 않음"),
        advisory_inferences_en=("The rat finding cannot be declared causally predictive for humans or dismissed as irrelevant without supporting evidence", "Negative rasH2 and micronucleus results do not automatically negate the rat C-cell finding", "A class benchmark defines questions but does not replace candidate-specific chronic toxicology and mechanistic evidence"),
    ),
    "TIR-202": ConsultingCase(
        case_id="TIR-202",
        title_ko="Tirzepatide–B12 조제 혼합물 — 새 불순물의 품질–독성 위험",
        title_en="Compounded tirzepatide–B12 — Quality-to-toxicity risk from a new impurity",
        customer_segment_ko="조제약국·Telehealth·품질팀·투자자",
        customer_segment_en="Compounder / telehealth company / quality team / investor",
        primary_objective_ko="새 반응성 불순물의 확인·qualification·제품조치 결정",
        primary_objective_en="Determine identification, qualification, and product action for a new reaction-derived impurity",
        engagement_type_ko="Quality-to-Toxicology Impurity Response",
        engagement_type_en="Quality-to-Toxicology Impurity Response",
        trigger_ko="Tirzepatide와 B12를 혼합한 조제품에서 반응 유래 불순물이 보고됐으나 임상적 영향은 알려지지 않음",
        trigger_en="A reaction-derived impurity has been reported in compounded tirzepatide–B12 products, but its clinical effects are unknown",
        decision_question_ko="혼합제품을 승인제품과 동등하다고 볼 수 있는가, 어떤 분석·독성·규제조치가 필요한가?",
        decision_question_en="Can the compounded combination be treated as equivalent to the approved product, and what analytical, toxicological, and regulatory actions are required?",
        development_concern_ko="높음·미확정 — 불순물 존재는 품질경고이나 독성·면역원성·PK의 임상적 영향은 아직 규명되지 않음",
        development_concern_en="High and unresolved — the impurity is a quality warning, while its actual toxicologic, immunogenic, and PK effects remain uncharacterized",
        automation_scope_ko="현재 EarlyTox 자동화 범위 밖; 분석화학·불순물 독성·규제 전문가 주도",
        automation_scope_en="Outside the current EarlyTox automation scope; expert-led analytical chemistry, impurity toxicology, and regulatory review",
        deliverables_ko=("독립적 구조확인·함량·lot survey 계획", "원인반응·안정성·공정 위험지도", "불순물 독성·면역원성·ADME qualification gap", "출하보류·회수·고객통지 의사결정 메모"),
        deliverables_en=("Independent structure-confirmation, quantitation, and lot-survey plan", "Reaction mechanism, stability, and process risk map", "Toxicology, immunogenicity, and ADME qualification gaps", "Quarantine, recall, and customer-notification decision memo"),
        recommended_actions_ko=("제조사 이해관계와 독립성을 고려해 제3기관에서 분석 재현", "불순물 분리·구조확인·reference standard 확보", "강제분해·혼합비·보관조건·시간에 따른 생성 kinetics 평가", "독성·면역원성·수용체활성·PK 영향과 환자 노출량을 단계적으로 확인"),
        recommended_actions_en=("Replicate the analysis at an independent laboratory while considering source conflicts of interest", "Isolate and characterize the impurity and establish a reference standard", "Assess formation kinetics by stress condition, mixing ratio, storage, and time", "Characterize toxicology, immunogenicity, receptor activity, PK, and patient exposure in stages"),
        service_tier_ko="고위험 자문 — 불순물·제품품질·환자안전 대응",
        service_tier_en="High-impact advisory — Impurity, product-quality, and patient-safety response",
        commercial_model_ko="단계형 프로젝트 — 확인분석 → qualification → 규제·시장조치",
        commercial_model_en="Phased project — confirmatory analysis → qualification → regulatory and market action",
        regulatory_anchors=("MOUNJARO-LABEL-2026", "TIR-B12-IMPURITY-2026", "LILLY-TIR-B12-LETTER-2026"),
        assessment_builder=None,
        related_case_ids=("TIR-201", "TIR-203", "IMP-012"),
        asset_ko="Tirzepatide",
        asset_en="Tirzepatide",
        case_basis_ko="2026년 동료심사 논문과 제조사 공개서한을 이용한 합성 품질위기 사례; 공식 규제결론이 아님",
        case_basis_en="Synthetic quality-crisis case informed by a 2026 peer-reviewed article and manufacturer open letter; not an official regulatory conclusion",
        public_evidence_ko=("2026년 동료심사 보고는 여러 출처의 tirzepatide–B12 조제품에서 반응 유래 불순물을 확인했다고 기술", "보고 저자들이 Lilly 직원이라는 이해관계를 공개했으며 임상적 영향은 알려지지 않았다고 설명", "승인 Mounjaro 제형과 조제 혼합제품은 동일한 조성·품질·검증상태로 가정할 수 없음"),
        public_evidence_en=("A 2026 peer-reviewed report described a reaction-derived impurity in tirzepatide–B12 compounded products from multiple sources", "The authors disclosed employment by Lilly and stated that the clinical impact was unknown", "Approved Mounjaro and compounded combination products cannot be assumed to have identical composition, quality, or validation status"),
        synthetic_assumptions_ko=("고객이 공급망의 다수 lot에서 tirzepatide–B12 혼합제품을 유통", "불순물 구조와 환자별 노출량은 아직 확인되지 않음", "독립시험과 lot 보존시료가 확보 가능"),
        synthetic_assumptions_en=("The client distributes tirzepatide–B12 compounded products across multiple lots", "The impurity structure and patient-level exposure are not yet confirmed", "Independent testing and retained lot samples are available"),
        advisory_inferences_ko=("불순물 검출은 곧 임상독성 입증은 아니지만 무시할 수 없는 품질 신호", "승인제품의 안전성 자료를 새로운 adduct에 자동 bridging할 수 없음", "분석 확인과 노출평가 전까지 위험을 낮게 분류하거나 제품동등성을 주장하기 어려움"),
        advisory_inferences_en=("Detection of an impurity does not prove clinical toxicity, but it is a material quality signal", "Safety evidence for the approved product cannot be automatically bridged to a new adduct", "Until analytical confirmation and exposure assessment are complete, a low-risk or equivalence claim is difficult to defend"),
    ),
    "TIR-203": ConsultingCase(
        case_id="TIR-203",
        title_ko="차세대 dual/triple agonist License-in — Tirzepatide class data를 어디까지 쓸 수 있는가?",
        title_en="Next-generation dual/triple agonist license-in — How far can tirzepatide class data be used?",
        customer_segment_ko="VC·제약 BD·중견 제약사",
        customer_segment_en="VC / pharma BD / mid-size pharmaceutical company",
        primary_objective_ko="Tirzepatide를 benchmark로 신규 incretin 자산의 독성개발 리스크 실사",
        primary_objective_en="Use tirzepatide as a benchmark to diligence toxicology-development risk for a new incretin asset",
        engagement_type_ko="Class-to-Candidate Nonclinical Due Diligence",
        engagement_type_en="Class-to-Candidate Nonclinical Due Diligence",
        trigger_ko="Seller가 tirzepatide의 승인경험을 근거로 신규 agonist의 독성위험이 낮다고 주장",
        trigger_en="The seller argues that tirzepatide's approval history substantially de-risks a new agonist",
        decision_question_ko="어떤 위험은 class evidence로 줄일 수 있고 어떤 위험은 신규 후보에서 다시 입증해야 하는가?",
        decision_question_en="Which risks can be informed by class evidence, and which must be re-established for the new candidate?",
        development_concern_ko="중간–높음 — receptor balance, biased signaling, 반감기, 조직노출, 면역원성 및 불순물은 후보별로 달라질 수 있음",
        development_concern_en="Moderate to high — receptor balance, biased signaling, half-life, tissue exposure, immunogenicity, and impurities may differ by candidate",
        automation_scope_ko="다자산·거래조건은 전문가 주도; NORA는 근거·gap·claim boundary 구조화",
        automation_scope_en="Multi-asset and transaction decisions are expert-led; NORA structures evidence, gaps, and claim boundaries",
        deliverables_ko=("Tirzepatide–신규후보 comparability matrix", "Class-known vs candidate-unknown risk map", "Data-room red flags와 milestone 조건", "추가 비임상·CMC·임상약리 실사계획"),
        deliverables_en=("Tirzepatide-to-candidate comparability matrix", "Class-known versus candidate-unknown risk map", "Data-room red flags and milestone conditions", "Additional nonclinical, CMC, and clinical-pharmacology diligence plan"),
        recommended_actions_ko=("GIPR/GLP-1R/GCGR potency·bias·occupancy를 직접 비교", "반감기·albumin binding·free exposure와 chronic exposure를 비교", "C-cell, GI, pancreas, gallbladder, renal-volume depletion, immunogenicity 위험을 후보별 검토", "Class bridge의 허용범위를 거래조건과 개발 milestone에 반영"),
        recommended_actions_en=("Directly compare GIPR/GLP-1R/GCGR potency, bias, and occupancy", "Compare half-life, albumin binding, free exposure, and chronic exposure", "Assess C-cell, GI, pancreatic, gallbladder, renal-volume-depletion, and immunogenicity risks for the candidate", "Translate the limits of the class bridge into transaction conditions and development milestones"),
        service_tier_ko="거래 자문 — Class-to-candidate 독성 실사",
        service_tier_en="Transaction advisory — Class-to-candidate toxicology diligence",
        commercial_model_ko="범위별 실사 프로젝트 — 자산 수·data room·의사결정 시점에 따라 견적",
        commercial_model_en="Scope-based diligence project — quoted by asset count, data-room depth, and decision timeline",
        regulatory_anchors=("MOUNJARO-LABEL-2026", "TIRZEPATIDE-MECHANISM-2020", "TIRZEPATIDE-STRUCTURE-2022"),
        assessment_builder=None,
        related_case_ids=("TIR-201", "TIR-202", "DD-008", "VC-011"),
        asset_ko="Tirzepatide",
        asset_en="Tirzepatide",
        case_basis_ko="승인제품의 공개 약리·라벨 자료를 신규 후보에 적용하려는 합성 License-in 실사 사례",
        case_basis_en="Synthetic license-in diligence case in which public pharmacology and label evidence from an approved product is proposed as a bridge to a new candidate",
        public_evidence_ko=("Tirzepatide는 GIPR 쪽으로 기울어진 dual GIP/GLP-1 agonism과 GLP-1R biased signaling을 보이는 것으로 보고", "현행 라벨은 C-cell, pancreatitis, GI, volume depletion 관련 AKI, gallbladder 등 여러 임상·비임상 위험을 포함", "승인제품의 자료는 class 질문을 제시하지만 다른 서열·수용체 균형·노출을 가진 후보의 직접 근거는 아님"),
        public_evidence_en=("Tirzepatide has been reported to show GIPR-favored dual GIP/GLP-1 agonism and biased GLP-1R signaling", "The current label includes C-cell, pancreatitis, GI, volume-depletion AKI, gallbladder, and other clinical/nonclinical risks", "Evidence for the approved product defines class questions but is not direct evidence for a candidate with a different sequence, receptor balance, or exposure"),
        synthetic_assumptions_ko=("신규 후보는 GLP-1/GIP/글루카곤의 삼중 agonist", "Seller는 tirzepatide와 유사한 peptide backbone과 weekly dosing을 강조", "장기독성·면역원성·불순물 자료는 초기 단계"),
        synthetic_assumptions_en=("The new candidate is a GLP-1/GIP/glucagon triagonist", "The seller emphasizes a tirzepatide-like peptide backbone and weekly dosing", "Chronic toxicology, immunogenicity, and impurity evidence remain early"),
        advisory_inferences_ko=("유사한 임상목적 또는 투여주기가 동일한 독성기전을 보장하지 않음", "Class evidence는 시험 우선순위를 줄 수 있지만 후보별 hazard와 exposure를 대체하지 못함", "거래가치는 효능뿐 아니라 남은 비임상 비용·기간·실패가능성을 반영해야 함"),
        advisory_inferences_en=("A similar clinical purpose or dosing interval does not guarantee an identical toxicity mechanism", "Class evidence can prioritize studies but cannot replace candidate-specific hazard and exposure evidence", "Transaction value should reflect remaining nonclinical cost, time, and failure probability in addition to efficacy"),
    ),
    "ASO-301": ConsultingCase(
        case_id="ASO-301",
        title_ko="차세대 BIRC5/Survivin ASO — 동물시험 전 sequence·class·면역위험 지도",
        title_en="Next-generation BIRC5/survivin ASO — Sequence, class, and immune-risk mapping before animal studies",
        customer_segment_ko="대학 Spin-out·초기 RNA 바이오텍",
        customer_segment_en="University spin-out / early RNA biotech",
        primary_objective_ko="후보서열 선정과 최소 비임상 독성패키지 설계",
        primary_objective_en="Select a candidate sequence and design a minimum nonclinical toxicity package",
        engagement_type_ko="Oligonucleotide EarlyTox & Sequence Risk Sprint",
        engagement_type_en="Oligonucleotide EarlyTox & Sequence Risk Sprint",
        trigger_ko="Survivin knockdown과 항종양 POC는 있으나 sequence-dependent off-target, chemistry/class effect 및 사람 관련성 자료가 부족",
        trigger_en="Survivin knockdown and antitumor proof of concept exist, but sequence-dependent off-target, chemistry/class effects, and human relevance are insufficiently characterized",
        decision_question_ko="어떤 AI/in silico·human NAM·노출근거가 다음 BIRC5 ASO 후보를 동물시험으로 넘기기에 충분한가?",
        decision_question_en="What AI/in silico, human NAM, and exposure evidence is sufficient to advance a BIRC5 ASO candidate into animal studies?",
        development_concern_ko="미정–높음 — on-target 정상조직 영향, human transcriptome off-target, complement·coagulation·platelet·간/신장 축적을 후보별로 확인해야 함",
        development_concern_en="Unknown to high — candidate-specific evaluation is needed for on-target normal-tissue effects, human-transcriptome off-targets, complement, coagulation, platelets, and liver/kidney accumulation",
        automation_scope_ko="현재 간독성 엔진은 일부 gap만 지원; 전체 ONT 판단은 전문가 주도",
        automation_scope_en="The current hepatotoxicity engine supports selected gaps; the full ONT assessment remains expert-led",
        deliverables_ko=("Product–sequence–hazard–assay ontology map", "Human transcriptome·genome off-target review plan", "Chemistry/class liability 및 species relevance matrix", "후보선정 Gate와 최초 GLP 전략"),
        deliverables_en=("Product–sequence–hazard–assay ontology map", "Human transcriptome/genome off-target review plan", "Chemistry/class-liability and species-relevance matrix", "Candidate-selection gates and initial GLP strategy"),
        recommended_actions_ko=("Justified in silico off-target search 후 orthogonal human-cell 확인", "정상조직 BIRC5 발현과 on-target exaggerated pharmacology 평가", "Complement·cytokine·coagulation/aPTT·platelet panel 구축", "간·신장 조직노출과 loading/반복용량 시나리오를 함께 설계"),
        recommended_actions_en=("Perform a justified in silico off-target search followed by orthogonal confirmation in human cells", "Assess normal-tissue BIRC5 expression and on-target exaggerated pharmacology", "Build complement, cytokine, coagulation/aPTT, and platelet panels", "Design liver/kidney exposure together with loading and repeat-dose scenarios"),
        service_tier_ko="진단형 — RNA 후보선정·EarlyTox 전략",
        service_tier_en="Diagnostic — RNA candidate selection and EarlyTox strategy",
        commercial_model_ko="프로젝트형 — 서열수·chemistry·전달체·시험계 범위에 따라 견적",
        commercial_model_en="Project-based — quoted by sequence count, chemistry, carrier, and assay scope",
        regulatory_anchors=("FDA-ONT-NONCLINICAL-2024-DRAFT", "FDA-ONT-CLINPHARM-2024", "LY2181308-PRECLINICAL-2011", "FDA-NAM-2026-DRAFT", "FDA-AI-2025-DRAFT"),
        assessment_builder=None,
        related_case_ids=("ASO-302", "ASO-303", "LAB-001"),
        asset_ko="BIRC5/Survivin antisense",
        asset_en="BIRC5/survivin antisense",
        case_basis_ko="합성 차세대 BIRC5 ASO 개발상황에 FDA ONT 초안과 LY2181308 공개 전임상 근거를 적용한 prospective 사례",
        case_basis_en="Prospective synthetic next-generation BIRC5 ASO case informed by FDA ONT draft guidance and public LY2181308 preclinical evidence",
        public_evidence_ko=("FDA 2024 ONT 초안은 on-target exaggerated pharmacology와 sequence-dependent off-target를 구분하고 정당화된 in silico·in vitro 평가를 논의", "ONT의 chemistry·metabolite·delivery element와 hybridization-independent class effects도 별도로 평가해야 함", "LY2181308 전임상 연구는 다양한 암세포와 xenograft에서 survivin downregulation 및 항종양 POC를 보고"),
        public_evidence_en=("The 2024 FDA ONT draft distinguishes on-target exaggerated pharmacology from sequence-dependent off-target effects and discusses justified in silico and in vitro assessment", "ONT chemistry, metabolites, delivery elements, and hybridization-independent class effects also require evaluation", "LY2181308 preclinical work reported survivin downregulation and antitumor proof of concept across cancer cells and xenografts"),
        synthetic_assumptions_ko=("신규 ASO의 서열과 chemistry는 LY2181308과 동일하지 않음", "고객은 3–5개 후보서열 중 하나를 선정하려 함", "사람 세포와 초기 분포자료를 확보할 수 있음"),
        synthetic_assumptions_en=("The new ASO sequence and chemistry are not identical to LY2181308", "The client is selecting one candidate from three to five sequences", "Human-cell and early distribution data can be generated"),
        advisory_inferences_ko=("역사적 POC는 표적 가설을 지지하지만 신규 sequence의 안전성을 보증하지 않음", "저분자 QSAR 또는 일반 AI 음성만으로 ONT off-target와 class liability를 배제할 수 없음", "동물종 선택은 sequence homology·target expression·PK를 함께 고려해야 함"),
        advisory_inferences_en=("Historical proof of concept supports the target hypothesis but does not establish the safety of a new sequence", "A small-molecule QSAR or generic AI negative result cannot exclude ONT off-target and class liabilities", "Species selection should integrate sequence homology, target expression, and PK"),
    ),
    "ASO-302": ConsultingCase(
        case_id="ASO-302",
        title_ko="LY2181308 회고분석 — 표적 억제가 확인됐는데 임상효과는 왜 이어지지 않았는가?",
        title_en="LY2181308 retrospective — Why did confirmed target engagement not translate into clinical benefit?",
        customer_segment_ko="제약 BD·포트폴리오 전략·Oncology biotech",
        customer_segment_en="Pharma BD / portfolio strategy / oncology biotech",
        primary_objective_ko="Target engagement와 임상효과를 분리해 자산·표적·전달전략을 재평가",
        primary_objective_en="Reassess the asset, target, and delivery strategy by separating target engagement from clinical benefit",
        engagement_type_ko="Translational Failure & Asset Strategy Review",
        engagement_type_en="Translational Failure & Asset Strategy Review",
        trigger_ko="First-in-human에서 tumor uptake와 survivin 억제가 확인됐지만 CRPC phase II에서 유효성 향상이 관찰되지 않음",
        trigger_en="Tumor uptake and survivin suppression were demonstrated in first-in-human work, but the CRPC phase II study did not improve efficacy",
        decision_question_ko="실패는 표적의 문제인가, 억제 깊이·기간·전달·환자선정·병용전략의 문제인가?",
        decision_question_en="Was the failure due to the target, depth/duration of suppression, delivery, patient selection, or combination strategy?",
        development_concern_ko="높은 번역 불확실성 — 분자표적 engagement는 있었지만 임상적 유효성 chain은 성립하지 않음",
        development_concern_en="High translational uncertainty — molecular target engagement occurred, but the chain to clinical efficacy was not established",
        automation_scope_ko="현재 EarlyTox 범위 밖; 번역약리·임상·포트폴리오 전문가 주도",
        automation_scope_en="Outside the current EarlyTox scope; expert-led translational pharmacology, clinical, and portfolio review",
        deliverables_ko=("Sequence→Exposure→Tumor uptake→Target knockdown→Apoptosis→Outcome 인과감사", "표적·약물·전달·환자선정 가설 분리", "재개발·중단·새 chemistry 전환 Gate", "후속 biomarker·trial design 옵션"),
        deliverables_en=("Causal audit from sequence to exposure, tumor uptake, target knockdown, apoptosis, and outcome", "Separation of target, drug, delivery, and patient-selection hypotheses", "Gates for redevelopment, termination, or new chemistry", "Follow-up biomarker and trial-design options"),
        recommended_actions_ko=("약 20% survivin 감소가 충분한 PD 깊이였는지 검토", "종양별 baseline expression·heterogeneity·knockdown 지속시간 분석", "Docetaxel 병용의 mechanistic timing과 exposure overlap 재평가", "Target engagement를 임상효과 증거로 과대해석하지 않도록 portfolio claim 수정"),
        recommended_actions_en=("Assess whether approximately 20% survivin reduction represented sufficient PD depth", "Analyze baseline expression, tumor heterogeneity, and duration of knockdown", "Reassess mechanistic timing and exposure overlap with docetaxel", "Revise portfolio claims so that target engagement is not overstated as evidence of clinical benefit"),
        service_tier_ko="전략 자문 — Translational failure·asset disposition",
        service_tier_en="Strategy advisory — Translational failure and asset disposition",
        commercial_model_ko="범위별 프로젝트 — 공개자료 review 또는 내부 raw data 포함 심층분석",
        commercial_model_en="Scope-based project — public-evidence review or deeper analysis with internal source data",
        regulatory_anchors=("LY2181308-PRECLINICAL-2011", "LY2181308-FIH-2010", "LY2181308-CRPC-P2-2014"),
        assessment_builder=None,
        related_case_ids=("ASO-301", "ASO-303", "DD-008"),
        asset_ko="BIRC5/Survivin antisense",
        asset_en="BIRC5/survivin antisense",
        case_basis_ko="실제 공개 LY2181308 전임상·First-in-human·CRPC phase II 결과를 이용한 회고적 번역사례",
        case_basis_en="Retrospective translational case using public LY2181308 preclinical, first-in-human, and CRPC phase II results",
        public_evidence_ko=("전임상 연구는 survivin knockdown, apoptosis 및 xenograft 항종양 효과를 보고", "First-in-human 연구는 750 mg에서 tumor accumulation과 약 20% survivin gene/protein 감소 및 긴 terminal half-life를 보고", "154명 CRPC phase II에서는 docetaxel/prednisone에 LY2181308을 추가해도 PFS·OS·PSA 반응 등 임상효과 개선이 확인되지 않음"),
        public_evidence_en=("Preclinical work reported survivin knockdown, apoptosis, and xenograft antitumor activity", "The first-in-human study reported tumor accumulation, about 20% reduction in survivin gene/protein expression at 750 mg, and a long terminal half-life", "In the 154-patient CRPC phase II study, adding LY2181308 to docetaxel/prednisone did not improve PFS, OS, or PSA response"),
        synthetic_assumptions_ko=("고객은 BIRC5 프로그램을 재시작하거나 차세대 chemistry로 전환할지 검토", "내부 종양 biopsy·PK/PD·subgroup 자료가 추가로 있을 수 있음", "의사결정은 단순 성공/실패가 아니라 가설별 salvageability를 평가"),
        synthetic_assumptions_en=("The client is deciding whether to restart a BIRC5 program or move to a next-generation chemistry", "Additional internal biopsy, PK/PD, and subgroup data may be available", "The decision evaluates salvageability by hypothesis rather than using a simple success/failure label"),
        advisory_inferences_ko=("표적 engagement는 필요조건일 수 있지만 임상효과의 충분조건은 아님", "표적 타당성, 전달, 억제정도, 환자선정과 병용전략을 분리해 실패원인을 진단해야 함", "과거 실패를 신규 ASO의 안전성 또는 무효성으로 자동 외삽하면 안 됨"),
        advisory_inferences_en=("Target engagement may be necessary but is not sufficient for clinical benefit", "Target validity, delivery, depth of suppression, patient selection, and combination strategy should be separated when diagnosing failure", "Historical failure should not be automatically extrapolated as proof of the safety or futility of a new ASO"),
    ),
    "ASO-303": ConsultingCase(
        case_id="ASO-303",
        title_ko="LY2181308 안전성 benchmark — 다음 Survivin ASO의 모니터링·중단기준 설계",
        title_en="LY2181308 safety benchmark — Designing monitoring and stopping rules for the next survivin ASO",
        customer_segment_ko="RNA 치료제 개발사·임상약리·독성·규제팀",
        customer_segment_en="RNA therapeutic sponsor / clinical pharmacology / toxicology / regulatory team",
        primary_objective_ko="역사적 임상 신호를 후보별 비임상·초기임상 위험관리로 번역",
        primary_objective_en="Translate historical clinical signals into candidate-specific nonclinical and early-clinical risk management",
        engagement_type_ko="Historical Safety Benchmark & First-in-Human Risk Plan",
        engagement_type_en="Historical Safety Benchmark & First-in-Human Risk Plan",
        trigger_ko="차세대 survivin ASO가 다른 sequence 또는 chemistry를 사용하지만 loading dose와 IV 투여를 계획",
        trigger_en="A next-generation survivin ASO uses a different sequence or chemistry but plans IV administration and loading doses",
        decision_question_ko="LY2181308의 complement·응고·혈소판·간 신호를 어떤 시험·모니터링·중단기준으로 반영해야 하는가?",
        decision_question_en="How should LY2181308 complement, coagulation, platelet, and liver signals inform studies, monitoring, and stopping rules?",
        development_concern_ko="중간–높음 — 역사적 신호는 후보별 인과가 확정된 class effect는 아니지만 무시할 수 없는 benchmark",
        development_concern_en="Moderate to high — the historical signals are not established as universal candidate-level class effects, but they are material benchmarks",
        automation_scope_ko="현재 EarlyTox 일부 모듈과 연결 가능하나 FIH risk plan은 전문가 주도",
        automation_scope_en="Selected EarlyTox modules are relevant, but the FIH risk plan remains expert-led",
        deliverables_ko=("역사적 adverse-event·laboratory signal matrix", "Sequence/chemistry/loading schedule comparability 평가", "비임상 complement·cytokine·coagulation·platelet·liver panel", "FIH sentinel·monitoring·stopping-rule 초안"),
        deliverables_en=("Historical adverse-event and laboratory-signal matrix", "Sequence, chemistry, and loading-schedule comparability assessment", "Nonclinical complement, cytokine, coagulation, platelet, and liver panel", "Draft FIH sentinel, monitoring, and stopping rules"),
        recommended_actions_ko=("Bb/C3a 또는 적절한 complement marker와 cytokine time-course 평가", "aPTT/PT-INR·platelet·lymphocyte·간효소·신기능을 exposure와 연결", "Loading dose와 infusion rate에 따른 acute reaction risk를 모델링", "Sentinel/staggering·관찰기간·중단기준을 chemistry-specific 자료로 정당화"),
        recommended_actions_en=("Assess Bb/C3a or appropriate complement markers and cytokine time courses", "Link aPTT/PT-INR, platelets, lymphocytes, liver enzymes, and renal function to exposure", "Model acute-reaction risk by loading dose and infusion rate", "Justify sentinel/staggering, observation periods, and stopping rules with chemistry-specific evidence"),
        service_tier_ko="FIH 자문 — RNA 임상진입 안전성·모니터링",
        service_tier_en="FIH advisory — RNA clinical-entry safety and monitoring",
        commercial_model_ko="전략 프로젝트 — 비임상 package review + FIH protocol/IB 자문",
        commercial_model_en="Strategy project — nonclinical package review plus FIH protocol/IB advisory",
        regulatory_anchors=("FDA-ONT-NONCLINICAL-2024-DRAFT", "FDA-ONT-CLINPHARM-2024", "LY2181308-FIH-2010", "LY2181308-JP-P1-2011"),
        assessment_builder=None,
        related_case_ids=("ASO-301", "ASO-302", "PREIND-009"),
        asset_ko="BIRC5/Survivin antisense",
        asset_en="BIRC5/survivin antisense",
        case_basis_ko="LY2181308 First-in-human 및 일본 phase I 안전성 신호를 가상 차세대 후보의 risk plan에 사용하는 회고·prospective 혼합 사례",
        case_basis_en="Combined retrospective/prospective case using LY2181308 first-in-human and Japanese phase I safety signals to design risk management for a synthetic next-generation candidate",
        public_evidence_ko=("First-in-human 연구에서는 flu-like syndrome, aPTT 연장, lymphopenia, thrombocytopenia와 complement activation 우려가 보고", "일본 phase I에서는 reversible grade 1/2 flu-like, PT-INR 연장, thrombocytopenia와 750 mg에서 reversible grade 3 ALT/AST/γ-GTP 상승 DLT가 보고", "긴 terminal half-life와 광범위 조직분포는 loading·maintenance schedule 및 회복성 해석에 중요"),
        public_evidence_en=("The first-in-human study reported flu-like syndrome, aPTT prolongation, lymphopenia, thrombocytopenia, and concern for complement activation", "The Japanese phase I study reported reversible grade 1/2 flu-like syndrome, prolonged PT-INR, thrombocytopenia, and a reversible grade 3 ALT/AST/γ-GTP DLT at 750 mg", "The long terminal half-life and extensive tissue distribution are important for loading/maintenance schedules and reversibility interpretation"),
        synthetic_assumptions_ko=("신규 후보는 LY2181308과 다른 sequence 또는 backbone chemistry를 사용", "IV loading regimen을 고려하지만 최종 schedule은 미정", "고객은 FIH 전에 NAM·동물·임상모니터링의 연결을 설계하려 함"),
        synthetic_assumptions_en=("The new candidate uses a sequence or backbone chemistry different from LY2181308", "An IV loading regimen is being considered but the final schedule is not fixed", "The client wants to connect NAM, animal, and clinical monitoring before FIH"),
        advisory_inferences_ko=("역사적 신호를 신규후보의 확정독성으로 간주해서는 안 되지만 사전질문에서 제외해서도 안 됨", "Chemistry·sequence·불순물·투여속도의 comparability가 class extrapolation 범위를 결정", "FIH 위험완화는 단일 NOAEL보다 acute infusion, 누적노출, laboratory kinetics를 함께 반영해야 함"),
        advisory_inferences_en=("Historical signals should not be treated as confirmed toxicities of the new candidate, but they should not be omitted from the prospective question set", "Comparability of chemistry, sequence, impurities, and infusion rate determines the limits of class extrapolation", "FIH risk mitigation should integrate acute infusion risk, accumulation, and laboratory kinetics rather than relying on a single NOAEL"),
    ),
}


def consulting_case_ids() -> list[str]:
    return list(CONSULTING_CASES)


def get_consulting_case(case_id: str) -> ConsultingCase:
    return CONSULTING_CASES[case_id]


def load_consulting_assessment(case_id: str) -> AssessmentInput:
    case = get_consulting_case(case_id)
    if case.assessment_builder is None:
        raise ValueError(f"Consulting case {case_id} is expert-led and does not have a single automated AssessmentInput.")
    return deepcopy(case.assessment_builder())


def consulting_segments(language: str = "ko") -> list[str]:
    return sorted({case.customer_segment(language) for case in CONSULTING_CASES.values()})


def consulting_objectives(language: str = "ko") -> list[str]:
    return sorted({case.primary_objective(language) for case in CONSULTING_CASES.values()})
