from __future__ import annotations

from copy import deepcopy

from .models import (
    AIModelCard,
    AssessmentInput,
    ContextOfUse,
    NAMAssayCard,
    ProductContext,
    SupportingEvidence,
)


def gp_l_ct_case() -> AssessmentInput:
    return AssessmentInput(
        context_of_use=ContextOfUse(
            objective="동물시험 범위 축소 가능성 평가",
            question_of_interest="현재 AI와 사람 기반 NAM 근거가 GP-L-CT의 초기 간독성 위험을 평가하고 후속 동물시험 범위를 줄이는 데 충분한가?",
            development_stage="후보물질 선정",
            target_endpoint="초기 간독성",
            intended_evidence_role="R4 · 동물시험 축소 지원",
            jurisdiction="연구용 / 내부 의사결정",
            model_influence=3,
            decision_consequence=3,
            decision_owner="독성책임자",
        ),
        product=ProductContext(
            product_name="GP-L-CT",
            modality="siRNA + 나노의약품",
            indication="항암 치료",
            active_substance="Survivin siRNA",
            target_mechanism="BIRC5 / transient gene silencing",
            carrier_formulation="Chitosan–Protamine–Lecithin–TPP hybrid nanocomplex",
            route="정맥투여",
            planned_dose="0.1–1.0 mg/kg",
            exposure_pattern="반복 노출",
            frequency="주 1회",
            treatment_duration="4주",
            target_organs="간, 비장",
            distribution_status="정성적 자료",
            test_article_representativeness="불명확",
        ),
        ai_model=AIModelCard(
            use_ai=True,
            model_name="Small-Molecule Hepato Classifier",
            model_version="v3.0",
            model_type="Machine learning classifier",
            endpoint="초기 간독성",
            result="음성 / 낮은 위험 예측",
            probability_percent=91,
            probability_type="원시 모델점수",
            endpoint_definition="문헌 기반 hepatotoxicity binary label; 중증도와 시간범위는 불명확",
            reference_standard="문헌 / 라벨 기반",
            label_quality="단일 출처 / 자동 라벨",
            missing_label_policy="불명확",
            time_window_defined=False,
            severity_threshold_defined=False,
            dataset_source="가상 vendor summary dataset",
            dataset_version="2025-Q4",
            training_sample_size=1200,
            positive_class_percent=None,
            split_strategy="무작위 분할",
            test_set_independence="부분 확인",
            leakage_assessment="미평가",
            duplicate_assessment="미평가",
            domain_modalities=["저분자"],
            external_validation="부분적으로 확인",
            external_validation_representativeness="부적절",
            sensitivity_percent=82,
            specificity_percent=76,
            false_negative_rate_percent=None,
            false_positive_rate_percent=24,
            ppv_percent=None,
            npv_percent=None,
            balanced_accuracy_percent=79,
            auroc=0.84,
            auprc=None,
            performance_confidence_intervals="불명확",
            decision_threshold=None,
            calibration_status="불명확",
            brier_score=None,
            calibration_slope=None,
            calibration_intercept=None,
            domain_status="자동 평가",
            nearest_neighbor_similarity_percent=None,
            ood_detection="불명확",
            prediction_interval="",
            prediction_uncertainty="높음",
            input_quality_verified=False,
            explainability_status="부분 연결",
            biological_plausibility="낮음",
            source="가상 모델 보고서",
            known_limitations="저분자 중심 학습; siRNA, 나노입자 전달체, 반복노출 및 간·비장 축적 미반영",
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
            positive_control="유효",
            negative_control="유효",
            carrier_only_control="미포함",
            active_only_control="미포함",
            protocol_completeness="부분적",
            nominal_exposure="0.1–100 µg/mL",
            measured_exposure="측정 안 됨",
            qivive_pbpk="없음",
            reproducibility="일부 확인",
            endpoints=["Cell viability / ATP"],
        ),
        supporting_evidence=SupportingEvidence(
            mechanistic_evidence=True,
            class_or_clinical_evidence=False,
            quantitative_biodistribution=False,
            pk_tk_evidence=False,
            existing_in_vivo_evidence=True,
            human_evidence=False,
            evidence_traceable=True,
            assertions_reviewed=False,
            expert_reviewed=False,
            version_locked=True,
            supporting_note="공개 연구에서 혈청 안정성, survivin knockdown 및 항종양 POC는 확인되었으나 정량적 biodistribution·반복독성·면역반응 자료는 제한적임.",
        ),
    )


def concordant_case() -> AssessmentInput:
    return AssessmentInput(
        context_of_use=ContextOfUse(
            objective="동물시험 범위 축소 가능성 평가",
            question_of_interest="검증된 AI 모델과 사람 간 spheroid 음성결과가 저분자 후보의 후속 동물 간독성시험을 정교화하거나 축소하는 데 충분한가?",
            development_stage="초기 비임상 개발",
            target_endpoint="초기 간독성",
            intended_evidence_role="R4 · 동물시험 축소 지원",
            jurisdiction="미국 FDA 사전미팅 준비",
            model_influence=3,
            decision_consequence=3,
            decision_owner="독성책임자",
        ),
        product=ProductContext(
            product_name="SM-NME-01",
            modality="저분자 NME",
            indication="대사질환",
            active_substance="Small molecule candidate",
            target_mechanism="Selective enzyme inhibitor",
            route="경구",
            planned_dose="10–50 mg/day",
            exposure_pattern="반복 노출",
            frequency="1일 1회",
            treatment_duration="4주",
            target_organs="간",
            human_cmax="2 µM",
            human_auc="20 µM·h",
            distribution_status="정량적 자료",
            test_article_representativeness="임상제품 대표성 확인",
        ),
        ai_model=AIModelCard(
            use_ai=True,
            model_name="Validated Hepato-AI",
            model_version="v5.2",
            endpoint="초기 간독성",
            result="음성 / 낮은 위험 예측",
            probability_percent=8,
            probability_type="보정된 확률",
            endpoint_definition="전문가 adjudication으로 확인된 임상 DILI 또는 중대한 간손상 binary endpoint",
            reference_standard="전문가 adjudication / 임상 기준",
            label_quality="전문가 검토·합의",
            missing_label_policy="미평가와 음성을 명확히 구분",
            time_window_defined=True,
            severity_threshold_defined=True,
            dataset_source="다기관 curated DILI dataset",
            dataset_version="2026.2",
            training_sample_size=4850,
            positive_class_percent=14.0,
            split_strategy="Scaffold 분할",
            test_set_independence="독립 확인",
            leakage_assessment="평가 완료 — 문제 없음",
            duplicate_assessment="중복 제거 / 관리",
            domain_modalities=["저분자"],
            external_validation="확인됨",
            external_validation_representativeness="현재 COU에 적절",
            sensitivity_percent=90,
            specificity_percent=86,
            false_negative_rate_percent=10,
            false_positive_rate_percent=14,
            ppv_percent=68,
            npv_percent=97,
            balanced_accuracy_percent=88,
            auroc=0.91,
            auprc=0.72,
            performance_confidence_intervals="보고됨",
            decision_threshold=0.35,
            calibration_status="검증됨",
            brier_score=0.08,
            calibration_slope=0.98,
            calibration_intercept=0.02,
            domain_status="In-domain",
            nearest_neighbor_similarity_percent=78,
            ood_detection="정량 평가 — In-domain",
            prediction_interval="5–12%",
            prediction_uncertainty="낮음",
            input_quality_verified=True,
            explainability_status="기전과 연결됨",
            biological_plausibility="높음",
            source="독립 외부검증 보고서",
            known_limitations="중증 간질환 환자군은 별도 검증 필요",
            code_commit="a1b2c3d",
            software_environment="Python 3.12; locked environment",
            training_data_hash="sha256:validated-hepato-dataset",
            last_validation_date="2026-07-15",
            drift_monitoring="운영 중",
            change_control="정의됨",
            lifecycle_plan="정의됨",
        ),
        nam_assay=NAMAssayCard(
            use_nam=True,
            nam_type="3D 간 Spheroid",
            system_origin="사람 유래",
            result="음성",
            cell_types=["간세포(Hepatocyte)", "Kupffer cell", "Stellate cell"],
            metabolic_competence="충분히 확인",
            immune_competence="충분",
            exposure_design="반복노출",
            positive_control="유효",
            negative_control="유효",
            carrier_only_control="해당 없음",
            active_only_control="해당 없음",
            protocol_completeness="완결",
            nominal_exposure="0.1–20 µM",
            measured_exposure="측정됨",
            qivive_pbpk="수행됨",
            reproducibility="Donor/lot/반복 재현성 확인",
            endpoints=[
                "Cell viability / ATP",
                "미토콘드리아 기능",
                "ALT / AST / GLDH",
                "CYP 대사기능",
            ],
        ),
        supporting_evidence=SupportingEvidence(
            mechanistic_evidence=True,
            class_or_clinical_evidence=True,
            quantitative_biodistribution=True,
            pk_tk_evidence=True,
            existing_in_vivo_evidence=False,
            human_evidence=True,
            evidence_traceable=True,
            assertions_reviewed=True,
            expert_reviewed=True,
            version_locked=True,
            expert_review_note="제한된 간독성 endpoint에서 용량군과 중복 sampling 축소를 검토할 수 있음.",
        ),
    )


def conflicting_case() -> AssessmentInput:
    return AssessmentInput(
        context_of_use=ContextOfUse(
            objective="AI·NAM·기존 근거 통합",
            question_of_interest="AI 음성예측과 사람 간 organoid 양성결과가 상충할 때 초기 간독성 위험과 다음 시험을 어떻게 결정해야 하는가?",
            development_stage="후보물질 선정",
            target_endpoint="초기 간독성",
            intended_evidence_role="R3 · 보조 근거",
            jurisdiction="연구용 / 내부 의사결정",
            model_influence=3,
            decision_consequence=4,
            decision_owner="프로그램 독성책임자",
        ),
        product=ProductContext(
            product_name="Conflict-NME-01",
            modality="저분자 NME",
            indication="신경계 질환",
            active_substance="Candidate X",
            target_mechanism="Mitochondrial pathway modulator",
            route="경구",
            exposure_pattern="반복 노출",
            human_cmax="5 µM",
            distribution_status="정성적 자료",
        ),
        ai_model=AIModelCard(
            use_ai=True,
            model_name="Hepato-ML",
            model_version="v2.1",
            endpoint="초기 간독성",
            result="음성 / 낮은 위험 예측",
            probability_percent=15,
            probability_type="보정된 확률",
            endpoint_definition="전문가 검토된 임상 DILI binary endpoint",
            reference_standard="전문가 adjudication / 임상 기준",
            label_quality="독립적 검토",
            missing_label_policy="미평가와 음성을 명확히 구분",
            time_window_defined=True,
            severity_threshold_defined=True,
            dataset_source="External DILI benchmark",
            dataset_version="2026.1",
            training_sample_size=2600,
            positive_class_percent=16.0,
            split_strategy="시간 분할",
            test_set_independence="독립 확인",
            leakage_assessment="평가 완료 — 문제 없음",
            duplicate_assessment="중복 제거 / 관리",
            domain_modalities=["저분자"],
            external_validation="확인됨",
            external_validation_representativeness="현재 COU에 적절",
            sensitivity_percent=80,
            specificity_percent=82,
            false_negative_rate_percent=20,
            false_positive_rate_percent=18,
            ppv_percent=58,
            npv_percent=94,
            balanced_accuracy_percent=81,
            auroc=0.86,
            auprc=0.61,
            performance_confidence_intervals="보고됨",
            decision_threshold=0.40,
            calibration_status="부분 검증",
            brier_score=0.13,
            calibration_slope=0.87,
            calibration_intercept=0.08,
            domain_status="In-domain",
            nearest_neighbor_similarity_percent=72,
            ood_detection="정량 평가 — In-domain",
            prediction_interval="9–24%",
            prediction_uncertainty="중간",
            input_quality_verified=True,
            explainability_status="기전과 연결됨",
            biological_plausibility="중간",
            source="외부검증 논문",
            code_commit="d4e5f6g",
            software_environment="Python 3.12; locked environment",
            training_data_hash="sha256:external-dili-benchmark",
            last_validation_date="2026-06-30",
            drift_monitoring="계획 있음",
            change_control="부분 정의",
            lifecycle_plan="부분 정의",
        ),
        nam_assay=NAMAssayCard(
            use_nam=True,
            nam_type="간 Organoid",
            system_origin="사람 유래",
            result="양성",
            cell_types=["간세포(Hepatocyte)", "Kupffer cell"],
            metabolic_competence="충분히 확인",
            immune_competence="부분적",
            exposure_design="반복노출",
            positive_control="유효",
            negative_control="유효",
            carrier_only_control="해당 없음",
            active_only_control="해당 없음",
            protocol_completeness="완결",
            measured_exposure="측정됨",
            qivive_pbpk="초기 연결",
            reproducibility="Donor/lot/반복 재현성 확인",
            endpoints=["Cell viability / ATP", "미토콘드리아 기능", "Omics signature"],
        ),
        supporting_evidence=SupportingEvidence(
            mechanistic_evidence=True,
            class_or_clinical_evidence=False,
            quantitative_biodistribution=False,
            pk_tk_evidence=True,
            existing_in_vivo_evidence=False,
            human_evidence=False,
            evidence_traceable=True,
            assertions_reviewed=True,
            expert_reviewed=False,
            version_locked=True,
        ),
    )


CASE_BUILDERS = {
    "GP-L-CT — 적용범위 밖 음성예측": gp_l_ct_case,
    "저분자 — 일치하는 고품질 근거": concordant_case,
    "저분자 — AI/NAM 상충": conflicting_case,
}


def load_case(name: str, language: str = "ko") -> AssessmentInput:
    builder = CASE_BUILDERS.get(name, gp_l_ct_case)
    case = deepcopy(builder())
    if language != "en":
        return case

    if name == "GP-L-CT — 적용범위 밖 음성예측":
        case.context_of_use.question_of_interest = (
            "Are the current AI and human-relevant NAM data sufficient to assess the early "
            "hepatotoxicity risk of GP-L-CT and support reduction of a follow-up animal study?"
        )
        case.context_of_use.decision_owner = "Toxicology lead"
        case.product.indication = "Oncology"
        case.ai_model.source = "Synthetic model report"
        case.ai_model.known_limitations = (
            "Training focused on small molecules; siRNA, nanoparticle carrier effects, repeated exposure, "
            "and liver/spleen accumulation were not represented."
        )
        case.supporting_evidence.supporting_note = (
            "Published work supports serum stability, survivin knockdown, and antitumor proof of concept, "
            "but quantitative biodistribution, repeat-dose toxicity, and immune-response evidence remain limited."
        )
    elif name == "저분자 — 일치하는 고품질 근거":
        case.context_of_use.question_of_interest = (
            "Are a validated AI model and concordant negative human liver-spheroid results sufficient to refine "
            "or reduce a follow-up animal hepatotoxicity study for this small-molecule candidate?"
        )
        case.context_of_use.decision_owner = "Toxicology lead"
        case.product.indication = "Metabolic disease"
        case.ai_model.source = "Independent external-validation report"
        case.ai_model.known_limitations = "Patients with severe liver disease require separate validation."
        case.supporting_evidence.expert_review_note = (
            "Within the defined hepatotoxicity endpoint, reduction of dose groups and duplicate sampling may be considered."
        )
    elif name == "저분자 — AI/NAM 상충":
        case.context_of_use.question_of_interest = (
            "How should early hepatotoxicity risk and the next study be determined when a negative AI prediction "
            "conflicts with a positive human liver-organoid result?"
        )
        case.context_of_use.decision_owner = "Program toxicology lead"
        case.product.indication = "Neurologic disease"
        case.ai_model.source = "External-validation publication"
    return case
