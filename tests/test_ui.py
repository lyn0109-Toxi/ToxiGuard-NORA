from __future__ import annotations

import sys
import types
import unittest


if "streamlit" not in sys.modules:
    stub = types.ModuleType("streamlit")
    stub.markdown = lambda *_args, **_kwargs: None
    sys.modules["streamlit"] = stub

from nora.ui import role_tone, safe


class UIDesignSystemTests(unittest.TestCase):
    def test_safe_escapes_dynamic_html(self):
        self.assertEqual(safe('<script>alert("x")</script>'), '&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;')

    def test_role_tone_supports_codes_and_numbers(self):
        self.assertEqual(role_tone("R4")["class"], "role-r4")
        self.assertEqual(role_tone(2)["label"], "R2")

    def test_unknown_role_falls_back_to_r0(self):
        self.assertEqual(role_tone("unknown")["class"], "role-r0")


if __name__ == "__main__":
    unittest.main()
