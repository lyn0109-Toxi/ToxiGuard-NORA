from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

REQUIRED_FILES = [
    SITE / "index.html",
    SITE / "app.js",
    SITE / "styles.css",
    SITE / "assets" / "logo.svg",
    SITE / "data" / "ontology.json",
    SITE / "data" / "gp_l_ct.json",
]


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED_FILES:
        if not path.exists():
            errors.append(f"Missing site file: {path.relative_to(ROOT)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("SITE VALIDATION: BLOCKED")
        return 1

    try:
        ontology = json.loads((SITE / "data" / "ontology.json").read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"Ontology JSON parse error: {exc}")
        ontology = {}

    expected_counts = {
        "chain": 12,
        "modules": 15,
        "roles": 6,
        "competencyQuestions": 15,
    }
    for key, expected in expected_counts.items():
        value = ontology.get(key)
        if not isinstance(value, list):
            errors.append(f"ontology.json: {key} must be a list")
        elif len(value) < expected:
            errors.append(f"ontology.json: {key} expected at least {expected}, found {len(value)}")

    html = (SITE / "index.html").read_text(encoding="utf-8")
    for asset in ["styles.css", "app.js", "assets/logo.svg"]:
        if asset not in html:
            errors.append(f"index.html does not reference {asset}")

    role_codes = {str(row.get("code", "")) for row in ontology.get("roles", []) if isinstance(row, dict)}
    if not {"R0", "R1", "R2", "R3", "R4", "R5"} <= role_codes:
        errors.append("ontology.json must expose Evidence Role R0-R5")

    js = (SITE / "app.js").read_text(encoding="utf-8")
    if not re.search(r"GP.?L.?CT", js, flags=re.IGNORECASE):
        errors.append("app.js must include the GP-L-CT demonstration")

    print("NORA ontology site validation")
    print(f"- modules: {len(ontology.get('modules', []))}")
    print(f"- causal nodes: {len(ontology.get('chain', []))}")
    print(f"- evidence roles: {len(ontology.get('roles', []))}")
    print(f"- competency questions: {len(ontology.get('competencyQuestions', []))}")
    for error in errors:
        print(f"ERROR: {error}")
    print("SITE VALIDATION: " + ("PASS" if not errors else "BLOCKED"))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
