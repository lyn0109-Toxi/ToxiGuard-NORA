from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from nora import __project_schema_version__
from nora.cases import concordant_case, conflicting_case, gp_l_ct_case
from nora.engine import evaluate
from nora.ontology import build_jsonld, build_turtle
from nora.projects import AuditEvent, ProjectBundle, project_json_bytes
from nora.reports import build_gap_csv, build_markdown_report, build_pdf_report

FIXED_TIME = "2026-08-26T00:00:00+00:00"
CASES = {
    "gp_l_ct": ("PRJ-GPLCT-EARLYTOX", "GP-L-CT EarlyTox", gp_l_ct_case),
    "concordant": ("PRJ-CONCORDANT-01", "Concordant EarlyTox", concordant_case),
    "conflict": ("PRJ-CONFLICT-01", "Conflicting Evidence EarlyTox", conflicting_case),
}


def normalize_audit(result, case_key: str) -> None:
    result.audit["assessment_id"] = f"NORA-SAMPLE-{case_key.upper().replace('_', '-')}"
    result.audit["assessment_timestamp_utc"] = FIXED_TIME


def build_case(case_key: str, project_id: str, project_name: str, builder) -> None:
    target = ROOT / "samples" / case_key
    target.mkdir(parents=True, exist_ok=True)

    inp = builder()
    result = evaluate(inp)
    normalize_audit(result, case_key)

    project = ProjectBundle(
        project_id=project_id,
        project_name=project_name,
        created_at_utc=FIXED_TIME,
        updated_at_utc=FIXED_TIME,
        owner="ToxiGuard NORA",
        description="Synthetic golden case for deterministic EarlyTox regression testing.",
        assessment_input=inp,
        documents=[],
        assertions=[],
        audit_events=[
            AuditEvent(
                event_id=f"AUD-{case_key.upper()}",
                timestamp_utc=FIXED_TIME,
                action="Golden case generated",
                actor="ToxiGuard NORA",
                detail=f"Schema {__project_schema_version__}",
            )
        ],
        last_result=result.to_dict(),
    )

    (target / "project.nora.json").write_bytes(project_json_bytes(project))
    (target / "report.md").write_text(
        build_markdown_report(inp, result, project_name=project_name), encoding="utf-8"
    )
    (target / "report.pdf").write_bytes(
        build_pdf_report(inp, result, project_name=project_name)
    )
    (target / "assessment.jsonld").write_text(
        json.dumps(
            build_jsonld(
                inp,
                result,
                project_id=project_id,
                project_name=project_name,
            ),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (target / "assessment.ttl").write_text(
        build_turtle(
            inp,
            result,
            project_id=project_id,
            project_name=project_name,
        ),
        encoding="utf-8",
    )
    (target / "gaps.csv").write_bytes(build_gap_csv(result))
    print(f"{case_key}: {result.evidence_role_code} / {len(result.data_gaps)} gaps")


def main() -> int:
    for case_key, args in CASES.items():
        build_case(case_key, *args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
