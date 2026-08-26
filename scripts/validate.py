from __future__ import annotations

import py_compile
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from nora import __version__


compile_targets = [
    ROOT / "streamlit_app.py",
    *sorted((ROOT / "nora").glob("*.py")),
    ROOT / "scripts" / "validate.py",
    ROOT / "scripts" / "repository_guard.py",
    ROOT / "scripts" / "build_release.py",
    ROOT / "scripts" / "validate_site.py",
    ROOT / "scripts" / "generate_samples.py",
    ROOT / "scripts" / "smoke_streamlit_stub.py",
]
compile_failures: list[str] = []
for path in compile_targets:
    try:
        py_compile.compile(str(path), doraise=True)
    except Exception as exc:
        compile_failures.append(f"{path.relative_to(ROOT)}: {exc}")


def run_script(name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / name)],
        capture_output=True,
        text=True,
    )


samples = run_script("generate_samples.py")

if (ROOT / ".git").exists():
    sample_diff = subprocess.run(
        ["git", "diff", "--quiet", "--", "samples"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
else:
    sample_diff = subprocess.CompletedProcess([], 0, "", "")

guard = run_script("repository_guard.py")
site = run_script("validate_site.py")

suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
result = unittest.TextTestRunner(verbosity=2).run(suite)

smoke = run_script("smoke_streamlit_stub.py")

report_dir = ROOT / "validation_reports"
report_dir.mkdir(exist_ok=True)
now = datetime.now(timezone.utc)
report_path = report_dir / f"validation_report_{now.strftime('%Y%m%dT%H%M%SZ')}.md"

lines = [
    f"# NORA EarlyTox v{__version__} Validation Report",
    "",
    f"- Timestamp UTC: {now.isoformat()}",
    f"- Golden-case generation status: {'PASS' if samples.returncode == 0 else 'FAIL'}",
    f"- Golden-case repository sync: {'PASS' if sample_diff.returncode == 0 else 'FAIL'}",
    f"- Repository guard status: {'PASS' if guard.returncode == 0 else 'FAIL'}",
    f"- Ontology site validation status: {'PASS' if site.returncode == 0 else 'FAIL'}",
    f"- Python compile failures: {len(compile_failures)}",
    f"- Unit tests run: {result.testsRun}",
    f"- Unit test failures: {len(result.failures)}",
    f"- Unit test errors: {len(result.errors)}",
    f"- Streamlit page smoke status: {'PASS' if smoke.returncode == 0 else 'FAIL'}",
    "",
]

for title, proc in [
    ("Golden-case generation output", samples),
    ("Repository guard output", guard),
    ("Ontology site validation output", site),
    ("Streamlit smoke output", smoke),
]:
    if proc.returncode != 0:
        lines.extend(
            [
                f"## {title}",
                "",
                "```",
                proc.stdout[-4000:] + proc.stderr[-2000:],
                "```",
                "",
            ]
        )

if compile_failures:
    lines.extend(["## Compile failures", *[f"- {item}" for item in compile_failures], ""])
if result.failures:
    lines.extend(["## Test failures", *[f"- {case}: {trace[-600:]}" for case, trace in result.failures], ""])
if result.errors:
    lines.extend(["## Test errors", *[f"- {case}: {trace[-600:]}" for case, trace in result.errors], ""])

status = (
    samples.returncode == 0
    and sample_diff.returncode == 0
    and guard.returncode == 0
    and site.returncode == 0
    and not compile_failures
    and result.wasSuccessful()
    and smoke.returncode == 0
)
lines.extend(["## Release Gate", "", "PASS" if status else "BLOCKED", ""])
report_path.write_text("\n".join(lines), encoding="utf-8")
print(f"Validation report: {report_path}")
raise SystemExit(0 if status else 1)
