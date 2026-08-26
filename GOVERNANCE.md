# NORA Scientific and Product Governance

## Decision ownership

NORA separates five responsibilities:

1. **Evidence extraction** — software or AI proposes structured assertions.
2. **Evidence review** — a qualified reviewer accepts, corrects, or rejects each assertion.
3. **Structural validation** — SHACL checks that required information exists and is well formed.
4. **Deterministic assessment** — versioned rules create gates, gaps, scores, and Evidence Role limits.
5. **Expert decision** — a human toxicology or regulatory expert approves high-impact conclusions.

## High-impact changes

The following require scientific review and regression tests:

- Evidence Role thresholds or caps
- reliable-negative conditions
- applicability-domain logic
- human-relevance logic
- exposure-translation rules
- animal reduction or replacement recommendations
- ontology classes/properties used by the rule engine
- SHACL shapes that block or permit assessment

## Required pull-request evidence

A scientific PR must include:

- the Question of Interest and Context of Use,
- affected rule or ontology IDs,
- rationale and source basis,
- expected direction of change,
- impacted golden cases,
- added or updated tests,
- residual uncertainty,
- reviewer and decision owner.

## Override policy

A human override must retain:

- original automated conclusion,
- revised conclusion,
- reviewer identity,
- timestamp,
- scientific rationale,
- additional evidence,
- ontology and rule-set versions.

Overrides never delete the original automated record.
