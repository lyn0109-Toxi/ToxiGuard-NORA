# Customer evidence review: first implementation

## Scope

This branch adds deterministic intake review support, not a trained ML model or a new scientific decision rule. The question is whether an extracted assertion is linked to a classified source in the current customer project before automatic application. No endpoint, modality, R0–R5 rule, or expert approval requirement is changed.

- Documents persist `source_kind`: unclassified, customer evidence, or external reference. Legacy documents default to unclassified.
- Document selection uses stable IDs, including when filenames are identical.
- The review queue shows pending human review, source issues, conflicting reviewed values, rejected candidates, and fields with no extracted candidates. The small intake field list is not a complete regulatory checklist.
- The UI blocks automatic application of reviewed assertions without a unique source document, matching name, source hash metadata, and excerpt found at its recorded location. Reviewed external references are not automatically applied as customer test results. Keep references proposed or rejected for this workflow rather than relabeling them to bypass the gate.
- No extracted candidate does not mean absent evidence or a negative finding. Source linkage is not scientific validation, and extraction confidence is not calibrated ML performance.
- Saving a source category clears traceability/review attestations and cached results. Previously applied assessment values are retained and require explicit review; this is not a provenance-aware rollback system.
- The optional `documents` argument preserves legacy callers of `apply_reviewed_assertions`; strict source checking is enforced by the app's application route. Manual input remains a separate workflow.

## Validation follow-up: 2026-11-09 UTC

- Supported runtimes: Python 3.11.18 and 3.12.16, each in a separate local virtual environment. Dependency consistency checks pass (42 packages each).
- Full validation passes on both runtimes: 61 tests, zero failures/errors; compilation, ontology site, golden-artifact reproduction, repository guard and 14 bilingual page smoke checks pass.
- Ten source-review regression tests cover legacy classification, persistence, rejected/pending/conflicting states, source IDs, malformed hash metadata, duplicate IDs/locations, altered excerpts, external references, approved application, and input nonmutation.
- Real Streamlit AppTest interactions pass in Korean and English on both runtimes: same-name document selection, unsaved versus saved classification, repeated save, apply/navigation, and reclassification blocking.
- Fixed callbacks that previously read language from session state outside rendering. They now capture the selected language for stable widget formatting.
- Fixed verified baseline defects: pyproject version 0.4.0 is aligned with package/VERSION 0.9.1; stale navigation-symbol expectation corrected; read-only CI workflow and scientific-review issue template added locally; generated golden samples refreshed without changing toxicity rules.
- Golden validation compares current artifact hashes before/after generation instead of Git HEAD, so reviewed uncommitted artifacts can be validated. Intentional stale-artifact rejection was checked separately; this is not a waiver of reproducibility.
- Source-code whitespace checks pass. Generated PDFs contain required PDF spacing; generated CSVs use CRLF and Markdown reports use hard-break spacing, so an unrestricted git whitespace check reports those artifact-format lines.

### Limits

- Visual browser QA remains incomplete. The browser extension failed while binding/navigating the new tab; native browser fallback was interrupted by active user control. UI actions stopped rather than interfere. No screenshot or visual-layout pass is claimed. The temporary localhost server was stopped.
- GitHub CI is configured but has not run remotely. No push, PR, commit or deployment was made.
- No scientific validation against real customer studies, calibrated ML evaluation, or regulatory approval is implied. R0–R5 logic is unchanged. Tests use synthetic evidence.
- Stored hash metadata is checked for format/presence, not cryptographic authenticity of imported project JSON; original raw file bytes are not retained by this workflow. Source-linked means linked to the current project's extracted text.
- Source reclassification clears attestations but does not roll back earlier input values. Manual review remains necessary.

## Review locally

Use `.venv311/bin/python` or `.venv312/bin/python`:

```
.venv311/bin/python -m unittest discover -s tests -p test_evidence_review.py -v
.venv311/bin/python scripts/verify_evidence_review_ui.py
.venv311/bin/python scripts/validate.py
.venv311/bin/streamlit run streamlit_app.py
```

The aggregate validator regenerates tracked samples. Current sample updates are intentional, reproducible outputs of the existing generator. Latest machine-generated reports are in `validation_reports/`; old blocked reports are historical and superseded by the supported-runtime runs.
