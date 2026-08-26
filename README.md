# ToxiGuard NORA

[![NORA Validation](https://github.com/lyn0109-Toxi/ToxiGuard-NORA/actions/workflows/ci.yml/badge.svg)](https://github.com/lyn0109-Toxi/ToxiGuard-NORA/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB)
![Streamlit](https://img.shields.io/badge/Streamlit-1.39%2B-FF4B4B)
![Ontology](https://img.shields.io/badge/Ontology-TG--PTO--ET-138A82)
![License](https://img.shields.io/badge/License-Proprietary-10243F)

**NORA** stands for **Nonclinical Ontology-based Risk Advisor**.

ToxiGuard NORA EarlyTox is an ontology-driven evidence-assurance workspace for evaluating whether AI- and New Approach Methodology (NAM) toxicity evidence is:

- technically credible,
- applicable to the candidate product,
- biologically relevant to humans,
- relevant to the intended exposure,
- concordant with independent evidence, and
- sufficient for a defined early drug-development decision.

> **AI predicts toxicity. NORA determines how far the evidence can be trusted.**

NORA does not certify product safety, grant animal-test waivers, predict regulatory approval, or replace expert toxicology judgment.

## Why NORA

Most AI toxicity tools stop at a prediction. NORA evaluates the evidence around that prediction:

```text
Question of Interest
→ Context of Use
→ Product & Exposure Context
→ AI / NAM Method
→ Method Execution
→ Evidence Assertion & Provenance
→ Credibility / Applicability / Human Relevance
→ Residual Uncertainty & Data Gaps
→ Evidence Role R0–R5
→ Next Evidence & Expert Decision
```

## Current scientific scope

The v0.4 vertical slice focuses on **early hepatotoxicity** for:

- small-molecule NMEs,
- oligonucleotides and siRNA,
- nanomedicines,
- biologics, and
- gene-therapy candidates.

Supported evidence types include AI/QSAR outputs, 2D human hepatocytes, cocultures, spheroids, organoids, liver-on-chip/MPS, PK/TK, biodistribution, mechanistic evidence, in vivo evidence, and human/class evidence.

## Evidence Role

| Role | Meaning |
|---|---|
| R0 | Not assessable |
| R1 | Hypothesis generating |
| R2 | Screening use |
| R3 | Supportive evidence |
| R4 | Reduction-supporting evidence |
| R5 | Candidate for replacement of a defined endpoint |

`R5` does **not** mean regulatory acceptance, full animal replacement, or product safety certification.

## Quick start

```bash
git clone https://github.com/lyn0109-Toxi/ToxiGuard-NORA.git
cd ToxiGuard-NORA
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open `http://localhost:8501`.

## Validation

```bash
python scripts/validate.py
python scripts/generate_samples.py  # Rebuild deterministic golden-case artifacts
```

The release gate covers deterministic role classification, evidence extraction, reviewed-assertion application, project persistence, Korean report generation, JSON-LD/Turtle output, and OWL/SHACL parsing.

## Repository map

```text
streamlit_app.py                 Korean Streamlit application
nora/models.py                   Typed assessment objects
nora/engine.py                   Deterministic rule engine
nora/evidence.py                 Document extraction and provenance
nora/assertions.py               Assertion proposal, review, and application
nora/projects.py                 JSON/SQLite project persistence and audit
nora/ontology.py                 JSON-LD and Turtle serialization
nora/reports.py                  Korean Markdown/PDF/CSV reporting
ontology/                        TG-PTO-ET OWL/RDF and SHACL
samples/                         Synthetic golden cases and outputs
tests/                           Scientific and software regression tests
docs/                            Architecture, governance, and deployment
```

## Governance principle

```text
Documents
→ AI proposes evidence assertions
→ Human accepts, corrects, or rejects
→ SHACL validates required structure
→ Deterministic rules assign Data Gaps and Evidence Role
→ LLM may draft an explanation
→ Expert approves high-impact conclusions
```

Only reviewed assertions should influence high-impact decisions.

## Korean documentation

See [README_KR.md](README_KR.md), [GOVERNANCE.md](GOVERNANCE.md), and the files in [`docs/`](docs/).

## License and use

This repository is publicly visible for authorized demonstration and review but is **not open source**. See [LICENSE.md](LICENSE.md), [SECURITY.md](SECURITY.md), and [CONTRIBUTING.md](CONTRIBUTING.md).
