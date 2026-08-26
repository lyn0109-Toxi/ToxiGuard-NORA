from __future__ import annotations

import unittest

from nora.cases import concordant_case, conflicting_case, gp_l_ct_case
from nora.engine import evaluate


class EarlyToxEngineTests(unittest.TestCase):
    def test_gp_l_ct_is_hypothesis_generating(self) -> None:
        result = evaluate(gp_l_ct_case())
        self.assertLessEqual(result.evidence_role, 1)
        codes = {gap.code for gap in result.data_gaps}
        self.assertIn("ET-G006", codes)
        self.assertIn("ET-G019", codes)

    def test_concordant_case_supports_reduction(self) -> None:
        result = evaluate(concordant_case())
        self.assertGreaterEqual(result.evidence_role, 4)
        self.assertEqual(result.residual_uncertainty, "낮음")

    def test_conflicting_case_is_capped(self) -> None:
        result = evaluate(conflicting_case())
        self.assertLessEqual(result.evidence_role, 2)
        self.assertIn("ET-G023", {gap.code for gap in result.data_gaps})

    def test_missing_question_blocks_assessment(self) -> None:
        case = gp_l_ct_case()
        case.context_of_use.question_of_interest = ""
        result = evaluate(case)
        self.assertEqual(result.evidence_role, 0)


if __name__ == "__main__":
    unittest.main()
