from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from nora import __version__
DIST = ROOT / "dist"
PACKAGE_ROOT = f"ToxiGuard-NORA-v{__version__}"
EXCLUDED_PARTS = {
    ".git",
    ".venv",
    ".nora_data",
    "validation_reports",
    "dist",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
}
EXCLUDED_SUFFIXES = {".pyc", ".db", ".sqlite", ".sqlite3"}


def include(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    return not any(part in EXCLUDED_PARTS for part in rel.parts) and path.suffix.lower() not in EXCLUDED_SUFFIXES


def main() -> int:
    DIST.mkdir(exist_ok=True)
    archive = DIST / f"ToxiGuard-NORA-v{__version__}.zip"
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(ROOT.rglob("*")):
            if path.is_file() and include(path):
                arcname = Path(PACKAGE_ROOT) / path.relative_to(ROOT)
                zf.write(path, arcname.as_posix())
    print(f"Release artifact: {archive}")
    print(f"Size bytes: {archive.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
