"""Deterministic review triage, not toxicity inference or scientific validation."""
from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

from .evidence import DocumentRecord, EvidenceAssertion

SOURCE_KINDS = ("unclassified", "customer_evidence", "external_reference")
REVIEWED = {"승인", "수정"}
# Intake prompts, not a complete or modality-specific regulatory checklist.
INTAKE_FIELDS = (
    "product.product_name", "product.modality", "product.route",
    "ai_model.model_name", "ai_model.external_validation",
    "nam_assay.nam_type", "nam_assay.measured_exposure",
    "supporting_evidence.pk_tk_evidence",
)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def source_issues(assertion: EvidenceAssertion, documents: Iterable[DocumentRecord]) -> list[str]:
    """Check a source against the current project, never just its display name."""
    if not assertion.source_document_id.strip():
        return ["source_document_missing_or_ambiguous"]
    matches = [d for d in documents if d.document_id == assertion.source_document_id]
    if len(matches) != 1:
        return ["source_document_missing_or_ambiguous"]
    document = matches[0]
    issues = []
    if document.source_kind != "customer_evidence":
        issues.append("external_reference" if document.source_kind == "external_reference" else "source_unclassified")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", document.sha256) or document.name != assertion.source_document_name:
        issues.append("source_metadata_mismatch")
    segments = [s for s in document.segments if s.location == assertion.source_location]
    excerpt = _normalize(assertion.source_excerpt)
    if not assertion.source_location.strip() or len(segments) != 1 or not excerpt or excerpt not in _normalize(segments[0].text):
        issues.append("source_excerpt_not_linked")
    return issues


def application_blockers(assertions: Iterable[EvidenceAssertion], documents: Iterable[DocumentRecord]) -> dict[str, list[str]]:
    """Reviewed claims must resolve to classified project evidence before application."""
    documents = list(documents)
    assertions = list(assertions)
    counts = Counter(a.assertion_id for a in assertions)
    blocked = {}
    for assertion in assertions:
        if assertion.review_status not in REVIEWED:
            continue
        issues = source_issues(assertion, documents)
        if not assertion.assertion_id or counts[assertion.assertion_id] != 1:
            issues.append("assertion_id_missing_or_ambiguous")
        if issues:
            blocked[assertion.assertion_id] = issues
    return blocked


def evidence_gap_rows(assertions: Iterable[EvidenceAssertion], documents: Iterable[DocumentRecord]) -> list[dict[str, str]]:
    """Show intake coverage without equating unextracted evidence with absence."""
    assertions, documents = list(assertions), list(documents)
    rows = []
    for path in sorted(set(INTAKE_FIELDS) | {a.field_path for a in assertions}):
        candidates = [a for a in assertions if a.field_path == path and a.review_status != "거절"]
        reviewed = [a for a in candidates if a.review_status in REVIEWED]
        values = {a.proposed_value.strip() for a in reviewed if a.value_type != "list"}
        if not candidates:
            state = "all_candidates_rejected" if any(a.field_path == path for a in assertions) else "not_extracted"
        elif len(values) > 1:
            state = "conflicting_reviewed_values"
        elif reviewed and any(source_issues(a, documents) for a in reviewed):
            state = "source_review_required"
        elif reviewed:
            state = "reviewed_source_linked"
        else:
            state = "human_review_pending"
        rows.append({"field_path": path, "review_state": state,
                     "assertion_ids": ", ".join(a.assertion_id for a in candidates),
                     "source_locations": "; ".join(f"{a.source_document_name} · {a.source_location}" for a in candidates)})
    return rows
