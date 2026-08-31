#!/usr/bin/env python3
from __future__ import annotations

import py_compile
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

COMPILE_TARGETS = [
    ROOT / "streamlit_app.py",
    *sorted((ROOT / "nora").glob("*.py")),
    ROOT / "scripts" / "smoke_streamlit_stub.py",
    ROOT / "scripts" / "validate_flagship_claims.py",
    ROOT / "scripts" / "validate_compact.py",
]


def run_script(relative_path: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / relative_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="nora-compact-validation-") as tmp:
        os.environ["NORA_DATA_DIR"] = tmp
        return _run_validation()


def _run_validation() -> int:
    compile_failures: list[str] = []
    for target in COMPILE_TARGETS:
        try:
            py_compile.compile(str(target), doraise=True)
        except Exception as exc:
            compile_failures.append(f"{target.relative_to(ROOT)}: {exc}")

    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    test_result = unittest.TextTestRunner(verbosity=2).run(suite)

    claim_audit = run_script("scripts/validate_flagship_claims.py")
    smoke = run_script("scripts/smoke_streamlit_stub.py")

    print("")
    print("NORA compact package validation")
    print(f"- Python compile failures: {len(compile_failures)}")
    print(f"- Unit tests run: {test_result.testsRun}")
    print(f"- Unit test failures: {len(test_result.failures)}")
    print(f"- Unit test errors: {len(test_result.errors)}")
    print(f"- Flagship claim audit: {'PASS' if claim_audit.returncode == 0 else 'FAIL'}")
    print(f"- Streamlit smoke runner: {'PASS' if smoke.returncode == 0 else 'FAIL'}")

    if compile_failures:
        print("")
        print("Compile failures")
        for failure in compile_failures:
            print(f"- {failure}")

    for title, proc in [
        ("Flagship claim audit output", claim_audit),
        ("Streamlit smoke output", smoke),
    ]:
        if proc.returncode != 0:
            print("")
            print(title)
            print(proc.stdout[-4000:])
            print(proc.stderr[-2000:])

    passed = (
        not compile_failures
        and test_result.wasSuccessful()
        and claim_audit.returncode == 0
        and smoke.returncode == 0
    )
    print("")
    print("COMPACT VALIDATION: " + ("PASS" if passed else "BLOCKED"))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
