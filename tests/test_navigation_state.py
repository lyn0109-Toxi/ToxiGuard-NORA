from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from scripts import smoke_streamlit_stub as smoke


ROOT = Path(__file__).resolve().parents[1]


class NavigationStateRegressionTests(unittest.TestCase):
    def tearDown(self):
        for key in [
            "NORA_DATA_DIR",
            "NORA_SMOKE_CLICK_KEY",
            "NORA_SMOKE_CLICK_LABEL",
            "NORA_SMOKE_LANGUAGE",
            "NORA_SMOKE_PAGE",
        ]:
            os.environ.pop(key, None)
        smoke.STUB.begin_run(clear_state=True)

    def test_streamlit_guard_blocks_same_run_widget_key_mutation(self):
        smoke.STUB.begin_run(clear_state=True)
        smoke.STUB.radio("workspace", ["overview", "assessment"], key="nav_page")

        with self.assertRaises(smoke.StreamlitAPIException):
            smoke.STUB.session_state.nav_page = "assessment"

    def test_project_overview_next_action_uses_pending_navigation(self):
        cases = [
            ("한국어", "권장 작업으로 이동"),
            ("English", "Go to Recommended Workspace"),
        ]
        for language, button_label in cases:
            with self.subTest(language=language), tempfile.TemporaryDirectory(prefix="nora-nav-test-") as tmp:
                os.environ["NORA_DATA_DIR"] = tmp
                os.environ["NORA_SMOKE_LANGUAGE"] = language
                os.environ["NORA_SMOKE_CLICK_LABEL"] = button_label

                with self.assertRaises(smoke.RerunRequested):
                    smoke.run_page("overview", clear_state=True)

                self.assertEqual(smoke.STUB.session_state["nav_page"], "overview")
                self.assertEqual(smoke.STUB.session_state["pending_nav_page"], "assessment")

                os.environ.pop("NORA_SMOKE_CLICK_LABEL", None)
                smoke.run_page("overview")

                self.assertEqual(smoke.STUB.session_state["nav_page"], "assessment")
                self.assertNotIn("pending_nav_page", smoke.STUB.session_state)

    def test_navigation_assignments_stay_out_of_page_handlers(self):
        source = (ROOT / "streamlit_app.py").read_text(encoding="utf-8")

        self.assertNotIn("st.session_state.nav_page =", source)
        self.assertIn("PENDING_NAV_PAGE_KEY", source)
        self.assertIn("_queue_navigation(next_page)", source)
        self.assertIn("key=NAV_PAGE_KEY", source)


if __name__ == "__main__":
    unittest.main()
