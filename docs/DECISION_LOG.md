# Product and Architecture Decision Log

## ADR-001 — NORA is an independent product repository

**Status:** Accepted
**Date:** 2026-08-26

NORA is managed separately from the broad ToxiGuard Platform repository. Shared capabilities may be reused later, but product scope, ontology, rules, releases, and validation remain independently versioned.

## ADR-002 — Early toxicity evidence assurance precedes CTA/IND readiness

**Status:** Accepted

The primary product question is whether AI/NAM evidence is credible and fit for a defined early-toxicity decision. CTA/IND readiness is a downstream application, not the first screen.

## ADR-003 — Deterministic rules assign Evidence Role

**Status:** Accepted

LLMs may extract assertions and draft explanations. Evidence Role, hard gates, and decision-affecting gaps are assigned by versioned deterministic logic.

## ADR-004 — Human review is mandatory for high-impact conclusions

**Status:** Accepted

R4, R5, Reliable Negative, animal-study reduction, and replacement-candidate conclusions require human review and audit records.

## ADR-005 — GitHub monorepo includes app and public ontology site

**Status:** Accepted

The Streamlit app remains at repository root. The explanatory TG-PTO-ET website is kept under `site/` and deployed through GitHub Pages.

## ADR-006 — Toxicity review app is named ToxiGuard NTR

**Status:** Accepted
**Date:** 2026-10-09

The toxicity evidence review app is named **ToxiGuard NTR**, where NTR means **Nonclinical Toxicity Review**. Its product description is "AI·NAM 기반 비임상 독성근거 검토". NORA remains the name of the broader strategy workspace integrating VCC, CTI, RF, and NTR. The current detailed assessment rules remain focused on early liver toxicity; the rename does not expand validated scope.

Update current app labels and product documentation while retaining existing repository paths, deployment URLs, Python module and environment variable names, project schemas (`nora-project-*`), and NORA homepage backup compatibility (`appId: nora`). Historical decisions, exported files, and user projects remain readable without migration. Public deployment and changes to the separately hosted NORA homepage require their own release steps.
