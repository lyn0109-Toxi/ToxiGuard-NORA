from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any, Iterable

from rdflib import Graph

from .evidence import DocumentRecord, EvidenceAssertion
from .models import AssessmentInput, AssessmentResult


CONTEXT = {
    "tg": "https://toxiguard.ai/ontology/earlytox/",
    "core": "https://toxiguard.ai/ontology/earlytox/core#",
    "decision": "https://toxiguard.ai/ontology/earlytox/decision#",
    "product": "https://toxiguard.ai/ontology/earlytox/product#",
    "tox": "https://toxiguard.ai/ontology/earlytox/toxicity#",
    "ai": "https://toxiguard.ai/ontology/earlytox/ai#",
    "nam": "https://toxiguard.ai/ontology/earlytox/nam#",
    "evidence": "https://toxiguard.ai/ontology/earlytox/evidence#",
    "assessment": "https://toxiguard.ai/ontology/earlytox/assessment#",
    "action": "https://toxiguard.ai/ontology/earlytox/action#",
    "governance": "https://toxiguard.ai/ontology/earlytox/governance#",
}


def _slug(value: str, fallback: str) -> str:
    value = re.sub(r"[^A-Za-z0-9가-힣_-]+", "_", value or "").strip("_")
    return value or fallback


def build_jsonld(
    inp: AssessmentInput,
    result: AssessmentResult,
    assertions: Iterable[EvidenceAssertion] | None = None,
    documents: Iterable[DocumentRecord] | None = None,
    project_id: str = "",
    project_name: str = "",
) -> dict[str, Any]:
    assertions = list(assertions or [])
    documents = list(documents or [])
    accepted = [item for item in assertions if item.review_status in {"승인", "수정"}]
    audit = result.audit
    assessment_id = audit.get("assessment_id", f"NORA-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")
    product_id = _slug(inp.product.product_name, "Unspecified_Product")

    evidence_nodes = [
        {
            "@id": f"tg:evidence/{document.document_id}",
            "@type": "evidence:EvidenceItem",
            "core:hasIdentifier": document.document_id,
            "core:hasName": document.name,
            "evidence:hasMediaType": document.media_type,
            "evidence:hasSHA256": document.sha256,
            "evidence:hasSegmentCount": len(document.segments),
            "evidence:hasWarning": document.warnings,
        }
        for document in documents
    ]
    assertion_nodes = [
        {
            "@id": f"tg:assertion/{item.assertion_id}",
            "@type": "evidence:EvidenceAssertion",
            "core:hasIdentifier": item.assertion_id,
            "evidence:hasCategory": item.category,
            "evidence:hasFieldPath": item.field_path,
            "evidence:hasLabel": item.label_ko,
            "evidence:hasObjectValue": item.proposed_value,
            "evidence:hasValueType": item.value_type,
            "evidence:supportedByEvidence": {"@id": f"tg:evidence/{item.source_document_id}"},
            "evidence:hasSourceLocation": item.source_location,
            "evidence:hasSourceExcerpt": item.source_excerpt,
            "evidence:hasExtractionConfidence": item.confidence,
            "evidence:hasReviewStatus": item.review_status,
            "evidence:hasReviewerNote": item.reviewer_note,
        }
        for item in accepted
    ]

    payload: dict[str, Any] = {
        "@context": CONTEXT,
        "@id": f"tg:assessment/{assessment_id}",
        "@type": "assessment:AssessmentRun",
        "core:hasIdentifier": assessment_id,
        "core:hasTimestamp": audit.get("assessment_timestamp_utc"),
        "core:isPartOfProject": {
            "@id": f"tg:project/{project_id or _slug(project_name, 'NORA_Project')}",
            "@type": "core:DevelopmentProgram",
            "core:hasName": project_name,
        },
        "decision:hasQuestionOfInterest": {
            "@type": "decision:QuestionOfInterest",
            "decision:hasQuestionText": inp.context_of_use.question_of_interest,
            "decision:hasDecisionObjective": inp.context_of_use.objective,
            "decision:hasDevelopmentStage": inp.context_of_use.development_stage,
            "decision:hasTargetEndpoint": inp.context_of_use.target_endpoint,
            "decision:hasIntendedEvidenceRole": inp.context_of_use.intended_evidence_role,
            "decision:hasJurisdiction": inp.context_of_use.jurisdiction,
            "decision:hasModelInfluence": inp.context_of_use.model_influence,
            "decision:hasDecisionConsequence": inp.context_of_use.decision_consequence,
            "decision:hasDecisionOwner": inp.context_of_use.decision_owner,
        },
        "assessment:evaluatesProduct": {
            "@id": f"tg:product/{product_id}",
            "@type": ["product:InvestigationalProduct", f"product:{_safe_class(inp.product.modality)}"],
            "core:hasName": inp.product.product_name,
            "product:hasModality": inp.product.modality,
            "product:hasIndication": inp.product.indication,
            "product:hasActiveSubstance": inp.product.active_substance,
            "product:hasTargetMechanism": inp.product.target_mechanism,
            "product:hasCarrier": inp.product.carrier_formulation,
            "product:hasAdministrationRoute": inp.product.route,
            "product:hasPlannedDose": inp.product.planned_dose,
            "product:hasExposurePattern": inp.product.exposure_pattern,
            "product:hasFrequency": inp.product.frequency,
            "product:hasTreatmentDuration": inp.product.treatment_duration,
            "product:hasTargetOrgans": inp.product.target_organs,
            "product:hasHumanCmax": inp.product.human_cmax,
            "product:hasHumanAUC": inp.product.human_auc,
            "product:hasDistributionStatus": inp.product.distribution_status,
            "product:hasTestArticleRepresentativeness": inp.product.test_article_representativeness,
        },
        "assessment:usesAIModelCard": {
            "@type": "ai:AIModelCard",
            "ai:useAI": inp.ai_model.use_ai,
            "ai:hasModelName": inp.ai_model.model_name,
            "ai:hasModelVersion": inp.ai_model.model_version,
            "ai:hasModelType": inp.ai_model.model_type,
            "ai:hasIntendedEndpoint": inp.ai_model.endpoint,
            "ai:hasPredictionResult": inp.ai_model.result,
            "ai:hasProbabilityPercent": inp.ai_model.probability_percent,
            "ai:hasDomainModalities": inp.ai_model.domain_modalities,
            "ai:hasExternalValidationStatus": inp.ai_model.external_validation,
            "ai:hasSensitivityPercent": inp.ai_model.sensitivity_percent,
            "ai:hasSpecificityPercent": inp.ai_model.specificity_percent,
            "ai:hasFalseNegativeRatePercent": inp.ai_model.false_negative_rate_percent,
            "ai:hasCalibrationStatus": inp.ai_model.calibration_status,
            "ai:hasDomainStatus": result.audit.get("ai_domain_status"),
            "ai:hasSource": inp.ai_model.source,
            "ai:hasKnownLimitation": inp.ai_model.known_limitations,
        },
        "assessment:usesNAMAssayCard": {
            "@type": "nam:NAMAssayCard",
            "nam:useNAM": inp.nam_assay.use_nam,
            "nam:hasNAMType": inp.nam_assay.nam_type,
            "nam:hasSystemOrigin": inp.nam_assay.system_origin,
            "nam:hasResult": inp.nam_assay.result,
            "nam:hasCellTypes": inp.nam_assay.cell_types,
            "nam:hasMetabolicCompetence": inp.nam_assay.metabolic_competence,
            "nam:hasImmuneCompetence": inp.nam_assay.immune_competence,
            "nam:hasExposureDesign": inp.nam_assay.exposure_design,
            "nam:hasPositiveControlStatus": inp.nam_assay.positive_control,
            "nam:hasNegativeControlStatus": inp.nam_assay.negative_control,
            "nam:hasCarrierOnlyControlStatus": inp.nam_assay.carrier_only_control,
            "nam:hasActiveOnlyControlStatus": inp.nam_assay.active_only_control,
            "nam:hasProtocolCompleteness": inp.nam_assay.protocol_completeness,
            "nam:hasNominalExposure": inp.nam_assay.nominal_exposure,
            "nam:hasMeasuredExposureStatus": inp.nam_assay.measured_exposure,
            "nam:hasQIVIVEStatus": inp.nam_assay.qivive_pbpk,
            "nam:hasReproducibilityStatus": inp.nam_assay.reproducibility,
            "nam:hasEndpoints": inp.nam_assay.endpoints,
        },
        "evidence:usesEvidenceItem": [{"@id": node["@id"]} for node in evidence_nodes],
        "evidence:usesAcceptedAssertion": [{"@id": node["@id"]} for node in assertion_nodes],
        "assessment:hasAssessmentResult": {
            "@type": "assessment:EvidenceRoleAssessment",
            "assessment:hasEvidenceRole": result.evidence_role_code,
            "assessment:hasEvidenceRoleName": result.evidence_role_name,
            "assessment:hasAnimalUseRecommendation": result.animal_use_status,
            "assessment:hasModelRisk": result.model_risk,
            "assessment:hasResidualUncertainty": result.residual_uncertainty,
            "assessment:hasEvidenceStreamCount": result.evidence_stream_count,
            "assessment:hasScores": result.scores,
            "assessment:hasGateResults": [gate.to_dict() for gate in result.gates],
            "assessment:hasDataGaps": [gap.to_dict() for gap in result.data_gaps],
            "assessment:hasRecommendations": result.recommendations,
        },
        "governance:hasAudit": result.audit,
        "@graph": [*evidence_nodes, *assertion_nodes],
    }
    return payload


def build_turtle(
    inp: AssessmentInput,
    result: AssessmentResult,
    assertions: Iterable[EvidenceAssertion] | None = None,
    documents: Iterable[DocumentRecord] | None = None,
    project_id: str = "",
    project_name: str = "",
) -> str:
    payload = build_jsonld(inp, result, assertions, documents, project_id, project_name)
    graph = Graph()
    graph.parse(data=json.dumps(payload, ensure_ascii=False), format="json-ld")
    serialized = graph.serialize(format="turtle")
    return serialized.decode("utf-8") if isinstance(serialized, bytes) else serialized


def _safe_class(label: str) -> str:
    mapping = {
        "저분자 NME": "ChemicalDrug",
        "올리고뉴클레오타이드": "OligonucleotideTherapeutic",
        "siRNA 치료제": "siRNAProduct",
        "나노의약품": "Nanomedicine",
        "siRNA + 나노의약품": "siRNANanomedicine",
        "바이오의약품": "BiologicalProduct",
        "유전자치료제": "GeneTherapyProduct",
    }
    return mapping.get(label, "InvestigationalProduct")
