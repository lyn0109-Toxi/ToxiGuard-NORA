# ToxiGuard-NORA v0.9.1 Compact Upload Manifest

Source package:

```text
/Users/leeyoung-nam/Downloads/ToxiGuard-NORA-GitHub-Upload-v0.9.1.zip
```

This compact package keeps only the Streamlit runtime, NORA Python modules, app data registries, ontology TTL files, and focused validation files. It excludes docs-heavy, samples-heavy, site, Docker, release, and non-runtime files from the full validated package.

Upload the contents of this folder into the existing repository root. Do not upload the outer folder itself.

## Commit 1

Message:

```text
feat: update NORA runtime to v0.9.1
```

Upload:

```text
streamlit_app.py
VERSION
requirements.txt
runtime.txt
packages.txt
.streamlit/config.toml
nora/__init__.py
nora/ai_credibility.py
nora/assertions.py
nora/cases.py
nora/consulting_cases.py
nora/engine.py
nora/evidence.py
nora/i18n.py
nora/models.py
nora/ontology.py
nora/projects.py
nora/reports.py
nora/ui.py
```

## Commit 2

Message:

```text
data: add v0.9.1 evidence and ontology registries
```

Upload:

```text
AI_CREDIBILITY_TEST_EVIDENCE.json
data/NORA_v0.9.1_Audit_Summary.json
data/NORA_v0.9.1_Claim_Validation_Matrix.csv
data/ai_credibility_rule_catalog.json
data/consulting_case_catalog.json
data/consulting_objective_router.json
data/consulting_reference_map.json
data/evidence_grading_vocabulary.json
data/flagship_case_matrix.json
data/flagship_claim_audit.json
data/flagship_reference_registry.json
data/rule_catalog.json
data/validated_reference_registry.json
ontology/tg_pto_et_core.ttl
ontology/tg_pto_et_shapes.ttl
```

## Commit 3

Message:

```text
test: add compact v0.9.1 validation set
```

Upload:

```text
scripts/smoke_streamlit_stub.py
scripts/validate_compact.py
scripts/validate_flagship_claims.py
tests/test_ai_credibility.py
tests/test_consulting_cases.py
tests/test_engine.py
tests/test_evidence.py
tests/test_flagship_claim_audit.py
tests/test_i18n.py
tests/test_projects.py
tests/test_reports_ontology.py
tests/test_rule_catalog.py
tests/test_ui.py
```

For a two-commit upload, combine Commit 2 and Commit 3.

## Excluded

```text
docs/
samples/
site/
.github/
Dockerfile
docker-compose.yml
Makefile
pyproject.toml
requirements-dev.txt
release and upload instruction reports
SHA256SUMS.txt
full-package FILE_MANIFEST files
README / governance / policy documents already present in the repository
```

## Check After Upload

```text
pip install -r requirements.txt
python scripts/validate_compact.py
streamlit run streamlit_app.py
```

Expected version:

```text
0.9.1
```
