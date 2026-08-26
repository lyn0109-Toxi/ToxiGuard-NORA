# Contributing to ToxiGuard NORA

This is a proprietary project. External contributions require prior written approval from the owner.

## Branch names

- `feature/<name>` — application capability
- `science/<name>` — ontology, scientific logic, or rule changes
- `fix/<name>` — bug fix
- `docs/<name>` — documentation only
- `release/<version>` — release preparation

## Before opening a pull request

```bash
python scripts/validate.py
```

For scientific changes, also document:

- Question of Interest
- Context of Use
- affected endpoint and modality
- affected rule IDs or ontology entities
- expected Evidence Role effect
- new/updated golden cases
- residual uncertainty
- expert-review requirement

## Coding principles

- deterministic rules decide the Evidence Role
- LLM output must remain proposed evidence until reviewed
- missing evidence is never treated as negative evidence
- out-of-domain predictions are not reliable negatives
- high-impact conclusions require human review
- all decision-relevant assertions require provenance
