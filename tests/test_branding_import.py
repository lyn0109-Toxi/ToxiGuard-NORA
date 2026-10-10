from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class BrandingImportRegressionTests(unittest.TestCase):
    def test_app_starts_with_package_cached_before_branding_was_added(self) -> None:
        """Streamlit reruns can retain an older nora package in sys.modules."""
        root = Path(__file__).resolve().parents[1]
        script = """
import os
import sys
import nora

from scripts.smoke_streamlit_stub import STUB, run_page
sys.modules['streamlit'] = STUB
import nora.ui

def obsolete_header(**kwargs):
    raise AssertionError('The app used a UI header cached before the rename')

nora.ui.render_brand_header = obsolete_header
rendered = []
STUB.markdown = lambda body, *args, **kwargs: rendered.append(str(body))

del nora.__app_name__
del nora.__app_full_name__
sys.modules.pop('nora.branding', None)
del nora.branding

for language in ('한국어', 'English'):
    os.environ['NORA_SMOKE_LANGUAGE'] = language
    for page in ('overview', 'consulting', 'documents', 'assertions', 'assessment', 'results', 'rules'):
        run_page(page, clear_state=True)

assert any('<h1>ToxiGuard NTR</h1>' in body for body in rendered)
"""
        with tempfile.TemporaryDirectory(prefix="ntr-branding-test-") as data_dir:
            completed = subprocess.run(
                [sys.executable, "-B", "-c", script],
                cwd=root,
                env={**os.environ, "NORA_DATA_DIR": data_dir, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                text=True,
                timeout=60,
            )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
