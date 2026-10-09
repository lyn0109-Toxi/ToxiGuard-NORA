"""Reading references for toxicity review, independent of assessment rules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "toxicity_guideline_references.json"


def load_guideline_references() -> list[dict[str, Any]]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))["references"]


def references_for_context(
    references: list[dict[str, Any]], *, modality: str = "", endpoint: str = ""
) -> list[dict[str, Any]]:
    """Select reading topics; this does not determine regulatory applicability."""
    core_ids = {"ICH-M3-R2", "ICH-S3A", "ICH-S3B", "ICH-S4"}
    tags: set[str] = set()
    modality_text = modality.casefold()
    endpoint_text = endpoint.casefold()
    modality_topics = {
        "oligonucleotide": ("올리고", "oligonucleotide", "sirna", "aso", "antisense"),
        "nanomaterial": ("나노", "nano", "liposome", "리포좀", "lnp"),
        "biologic": ("바이오", "biologic", "antibody", "항체", "protein"),
        "gene_therapy": ("유전자치료", "gene therapy", "세포치료", "cell therapy"),
    }
    endpoint_topics = {
        "cardiac": ("심장", "cardiac", "cardiotox", "qt"),
        "immunotoxicity": ("면역", "immunotox"),
        "genotoxicity": ("유전독성", "genotox"),
    }
    for tag, terms in modality_topics.items():
        if any(term in modality_text for term in terms):
            tags.add(tag)
    for tag, terms in endpoint_topics.items():
        if any(term in endpoint_text for term in terms):
            tags.add(tag)
    return [ref for ref in references if ref["id"] in core_ids or tags.intersection(ref["tags"])]


def search_guideline_references(
    references: list[dict[str, Any]], query: str
) -> list[dict[str, Any]]:
    query = query.strip().casefold()
    if not query:
        return references
    number = query.strip("[]# ")
    if number.isdecimal():
        return [ref for ref in references if ref["number"] == int(number)]
    return [
        ref for ref in references
        if query in " ".join([
            ref["id"], ref["issuer"], ref["short_label"], ref["title"],
            *ref["summary"].values(), *ref["relevance"].values(), *ref["tags"],
        ]).casefold()
    ]
