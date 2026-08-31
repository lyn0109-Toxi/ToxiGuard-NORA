from __future__ import annotations

import unittest

from nora.cases import concordant_case, gp_l_ct_case
from nora.engine import evaluate


class AIToxicityCredibilityTests(unittest.TestCase):
    def test_concordant_case_has_high_prediction_reliability(self) -> None:
        result = evaluate(concordant_case())
        self.assertGreaterEqual(result.evidence_role, 4)
        self.assertEqual(result.prediction_reliability, "높음")
        self.assertEqual(result.toxicity_direction, "일관된 음성 신호")
        self.assertTrue(result.development_concern.startswith("낮음"))
        self.assertGreaterEqual(float(result.ai_credibility_profile["데이터 신뢰성"]), 3.0)

    def test_gp_l_ct_is_out_of_domain_and_not_reliable_negative(self) -> None:
        case = gp_l_ct_case()
        result = evaluate(case)
        codes = {gap.code for gap in result.data_gaps}
        self.assertLessEqual(result.evidence_role, 1)
        self.assertIn(result.prediction_reliability, {"낮음", "평가 불가"})
        self.assertIn("AI-G018", codes)
        self.assertIn("AI-G026", codes)
        self.assertIn("AI-G030", codes)
        self.assertTrue(result.development_concern.startswith(("미정", "중간", "높음")))

    def test_confirmed_data_leakage_caps_role_at_r1(self) -> None:
        case = concordant_case()
        case.ai_model.leakage_assessment = "누수 확인"
        result = evaluate(case)
        self.assertLessEqual(result.evidence_role, 1)
        self.assertIn("AI-G007", {gap.code for gap in result.data_gaps})

    def test_missing_ground_truth_caps_high_impact_use(self) -> None:
        case = concordant_case()
        case.ai_model.endpoint_definition = ""
        case.ai_model.reference_standard = "불명확"
        case.ai_model.label_quality = "불명확"
        case.ai_model.missing_label_policy = "불명확"
        case.ai_model.time_window_defined = False
        case.ai_model.severity_threshold_defined = False
        result = evaluate(case)
        self.assertLessEqual(result.evidence_role, 2)
        self.assertIn("AI-G010", {gap.code for gap in result.data_gaps})
        self.assertIn("AI-G011", {gap.code for gap in result.data_gaps})

    def test_uncalibrated_percentage_is_not_treated_as_probability(self) -> None:
        case = concordant_case()
        case.ai_model.probability_type = "원시 모델점수"
        case.ai_model.calibration_status = "미검증"
        case.ai_model.brier_score = None
        case.ai_model.calibration_slope = None
        case.ai_model.calibration_intercept = None
        result = evaluate(case)
        codes = {gap.code for gap in result.data_gaps}
        self.assertIn("AI-G026", codes)
        self.assertIn("AI-G027", codes)
        self.assertLessEqual(result.evidence_role, 3)

    def test_positive_signal_does_not_become_reduction_support(self) -> None:
        case = concordant_case()
        case.ai_model.result = "양성 / 위험 신호"
        case.nam_assay.result = "양성"
        case.ai_model.ppv_percent = 75
        result = evaluate(case)
        self.assertLessEqual(result.evidence_role, 3)
        self.assertEqual(result.toxicity_direction, "일관된 양성 신호")
        self.assertTrue(result.development_concern.startswith(("중간", "높음")))
        self.assertNotEqual(result.animal_use_status, "제한적 축소 지원")
        self.assertNotEqual(result.animal_use_status, "특정 시험 대체 후보")

    def test_prediction_profile_has_six_dimensions(self) -> None:
        case = concordant_case()
        result = evaluate(case)
        self.assertEqual(len(result.ai_credibility_profile), 6)
        self.assertIn("Endpoint·Ground Truth 적절성", result.ai_credibility_profile)
        self.assertIn("Lifecycle·Governance", result.ai_credibility_profile)


if __name__ == "__main__":
    unittest.main()
