# Changelog

All notable changes to ToxiGuard NORA are documented here.

## [0.4.0] - 2026-08-26

### Added

- dedicated GitHub repository layout
- repository governance, security, contribution, and roadmap documents
- scientific issue templates and pull-request checklist
- GitHub Actions CI for Python 3.11 and 3.12
- centralized app, ontology, rule-set, and project-schema versions
- GitHub publication helper scripts

### Carried forward from 0.3

- Korean Streamlit Evidence Assurance workspace
- document extraction and provenance
- reviewed Evidence Assertion workflow
- deterministic EarlyTox rule engine
- Evidence Role R0–R5
- Korean Markdown/PDF/CSV reporting
- JSON-LD and Turtle export
- SQLite and project JSON persistence
- TG-PTO-ET OWL/RDF and SHACL

## 0.4.1 - Bilingual language hotfix

- Added a top-right `한국어 | English` language switch.
- Preserved project, document, assertion, and assessment state during language changes.
- Added bilingual UI labels, Golden Cases, Markdown/PDF reports, and Data Gap CSV exports.
- Unified the footer regulatory notice with the same `nora_language` session-state key.
- Added bilingual regression tests and two-language Streamlit smoke coverage.
