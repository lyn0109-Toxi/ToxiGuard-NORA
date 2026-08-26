from __future__ import annotations

import json
import re
import sys
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "README_KR.md",
    "VERSION",
    "LICENSE.md",
    "SECURITY.md",
    "streamlit_app.py",
    "requirements.txt",
    "nora/__init__.py",
    "nora/engine.py",
    "data/rule_catalog.json",
    "ontology/tg_pto_et_core.ttl",
    "ontology/tg_pto_et_shapes.ttl",
    ".github/workflows/ci.yml",
    ".github/ISSUE_TEMPLATE/scientific_validation.yml",
    "scripts/generate_samples.py",
    "scripts/configure_github.sh",
    "site/index.html",
    "site/data/ontology.json",
]

FORBIDDEN_NAMES = {
    ".env",
    "secrets.toml",
    "projects.db",
    "credentials.json",
    "service-account.json",
}
FORBIDDEN_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".pem", ".key", ".p12", ".pfx"}
SECRET_PATTERNS = {
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "GitHub personal token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "Private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}
TEXT_SUFFIXES = {".py", ".md", ".txt", ".toml", ".yml", ".yaml", ".json", ".ttl", ".csv", ".sh"}
EXCLUDED_DIRS = {".git", ".venv", ".nora_data", "dist", "validation_reports", "__pycache__", ".pytest_cache", ".ruff_cache"}


def iter_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIRS for part in path.relative_to(ROOT).parts):
            continue
        yield path


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            errors.append(f"Missing required file: {rel}")

    for path in iter_files():
        rel = path.relative_to(ROOT)
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"Forbidden local/secret file: {rel}")
        if path.suffix.lower() in TEXT_SUFFIXES and path.stat().st_size <= 2_000_000:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for label, pattern in SECRET_PATTERNS.items():
                if pattern.search(text):
                    errors.append(f"Potential {label} in {rel}")

    try:
        catalog = json.loads((ROOT / "data" / "rule_catalog.json").read_text(encoding="utf-8"))
        if not isinstance(catalog, list) or not catalog:
            errors.append("data/rule_catalog.json must be a non-empty list")
        else:
            ids = [str(item.get("rule_id", "")) for item in catalog]
            if any(not item for item in ids):
                errors.append("Every rule catalog entry must have Rule ID")
            if len(ids) != len(set(ids)):
                errors.append("Rule IDs must be unique")
    except Exception as exc:
        errors.append(f"Rule catalog parse error: {exc}")

    try:
        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        project_version = pyproject["project"]["version"]
        version_text = (ROOT / "nora" / "__init__.py").read_text(encoding="utf-8")
        match = re.search(r'__version__\s*=\s*"([^"]+)"', version_text)
        package_version = match.group(1) if match else ""
        if project_version != package_version:
            errors.append(f"Version mismatch: pyproject={project_version}, nora={package_version}")
        version_file = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        if version_file != package_version:
            errors.append(f"Version mismatch: VERSION={version_file}, nora={package_version}")
    except Exception as exc:
        errors.append(f"Version metadata error: {exc}")

    try:
        tracked_local_data = subprocess.run(
            ["git", "ls-files", ".nora_data"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
        if tracked_local_data:
            errors.append(".nora_data must not be tracked by Git")
        elif (ROOT / ".nora_data").exists():
            warnings.append("Local .nora_data directory exists but is ignored and not tracked")
    except OSError:
        if (ROOT / ".nora_data").exists():
            warnings.append("Local .nora_data directory exists; Git tracking could not be checked")
    if not (ROOT / ".gitignore").exists():
        errors.append(".gitignore is required")

    print("NORA repository guard")
    print(f"- scanned files: {sum(1 for _ in iter_files())}")
    print(f"- warnings: {len(warnings)}")
    print(f"- errors: {len(errors)}")
    for item in warnings:
        print(f"WARN: {item}")
    for item in errors:
        print(f"ERROR: {item}")
    print("REPOSITORY GUARD: " + ("PASS" if not errors else "BLOCKED"))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
