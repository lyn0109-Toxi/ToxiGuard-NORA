from __future__ import annotations

import json
import unittest
from pathlib import Path

from nora.consulting_cases import CONSULTING_CASES, load_consulting_assessment
from nora.engine import evaluate


ROOT = Path(__file__).resolve().parents[1]


class ConsultingCaseLibraryTests(unittest.TestCase):
    def test_catalog_contains_diverse_customer_objectives(self):
        self.assertEqual(len(CONSULTING_CASES), 21)
        segments = {case.customer_segment_ko for case in CONSULTING_CASES.values()}
        objectives = {case.primary_objective_ko for case in CONSULTING_CASES.values()}
        self.assertGreaterEqual(len(segments), 14)
        self.assertGreaterEqual(len(objectives), 18)

    def test_engine_supported_cases_match_expected_roles(self):
        for case_id, case in CONSULTING_CASES.items():
            if not case.is_engine_supported:
                continue
            result = evaluate(load_consulting_assessment(case_id))
            self.assertGreaterEqual(result.evidence_role, case.expected_role_min, case_id)
            self.assertLessEqual(result.evidence_role, case.expected_role_max, case_id)

    def test_expert_led_cases_are_explicit(self):
        expert_ids = {case_id for case_id, case in CONSULTING_CASES.items() if not case.is_engine_supported}
        expected = {
            "VC-011", "IMP-012",
            "TAC-101", "TAC-102", "TAC-103",
            "TIR-201", "TIR-202", "TIR-203",
            "ASO-301", "ASO-302", "ASO-303",
        }
        self.assertEqual(expert_ids, expected)
        for case_id in expert_ids:
            self.assertTrue(
                "전문가" in CONSULTING_CASES[case_id].automation_scope_ko
                or "전문가" in CONSULTING_CASES[case_id].development_concern_ko,
                case_id,
            )

    def test_positive_signal_separates_role_from_concern(self):
        case = CONSULTING_CASES["GT-005"]
        result = evaluate(load_consulting_assessment("GT-005"))
        self.assertEqual(result.evidence_role_code, "R3")
        self.assertIn("높음", case.development_concern_ko)

    def test_portfolio_case_links_three_different_decision_profiles(self):
        case = CONSULTING_CASES["VC-011"]
        self.assertEqual(set(case.related_case_ids), {"LAB-001", "RED-004", "DD-008"})
        roles = {
            evaluate(load_consulting_assessment(case_id)).evidence_role_code
            for case_id in case.related_case_ids
        }
        self.assertEqual(roles, {"R1", "R2", "R4"})

    def test_flagship_assets_have_three_cases_each(self):
        expected = {
            "Tacrolimus": {"TAC-101", "TAC-102", "TAC-103"},
            "Tirzepatide": {"TIR-201", "TIR-202", "TIR-203"},
            "BIRC5/Survivin antisense": {"ASO-301", "ASO-302", "ASO-303"},
        }
        for asset, ids in expected.items():
            actual = {case_id for case_id, case in CONSULTING_CASES.items() if case.asset_ko == asset}
            self.assertEqual(actual, ids, asset)

    def test_flagship_cases_separate_source_facts_assumptions_and_inference(self):
        for case_id in [
            "TAC-101", "TAC-102", "TAC-103",
            "TIR-201", "TIR-202", "TIR-203",
            "ASO-301", "ASO-302", "ASO-303",
        ]:
            case = CONSULTING_CASES[case_id]
            self.assertTrue(case.case_basis_ko, case_id)
            self.assertGreaterEqual(len(case.public_evidence_ko), 3, case_id)
            self.assertGreaterEqual(len(case.synthetic_assumptions_ko), 3, case_id)
            self.assertGreaterEqual(len(case.advisory_inferences_ko), 3, case_id)
            self.assertGreaterEqual(len(case.regulatory_anchors), 2, case_id)

    def test_reference_registry_covers_every_case_anchor(self):
        registry_path = ROOT / "data" / "consulting_reference_map.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        missing = sorted({
            ref_id
            for case in CONSULTING_CASES.values()
            for ref_id in case.regulatory_anchors
            if ref_id not in registry
        })
        self.assertEqual(missing, [])

    def test_cautionary_scientific_boundaries_are_explicit(self):
        self.assertIn("사람 관련성 미정", CONSULTING_CASES["TIR-201"].development_concern_ko)
        self.assertIn("임상적 영향", CONSULTING_CASES["TIR-202"].development_concern_ko)
        self.assertTrue(any("임상효과" in item for item in CONSULTING_CASES["ASO-302"].public_evidence_ko))
        self.assertTrue(any("확정독성" in item for item in CONSULTING_CASES["ASO-303"].advisory_inferences_ko))
        self.assertTrue(any("특정 제품" in item for item in CONSULTING_CASES["TAC-101"].public_evidence_ko))


if __name__ == "__main__":
    unittest.main()
