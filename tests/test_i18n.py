from __future__ import annotations

import unittest

from nora.cases import load_case
from nora.engine import evaluate
from nora.i18n import audit_action_label, audit_detail_label, localize_result, page_label, value_label
from nora.reports import build_gap_csv, build_markdown_report, build_pdf_report


class BilingualTests(unittest.TestCase):
    def test_page_and_option_labels(self) -> None:
        self.assertEqual(page_label("overview", "ko"), "프로젝트 개요")
        self.assertEqual(page_label("overview", "en"), "Project Overview")
        self.assertEqual(page_label("consulting", "ko"), "컨설팅 스튜디오")
        self.assertEqual(page_label("consulting", "en"), "Advisory Studio")
        self.assertEqual(value_label("siRNA + 나노의약품", "en"), "siRNA + nanomedicine")
        self.assertEqual(value_label("음성 / 낮은 위험 예측", "en"), "Negative / low-risk prediction")

    def test_english_result_localization(self) -> None:
        inp = load_case("GP-L-CT — 적용범위 밖 음성예측", "en")
        result = evaluate(inp)
        localized = localize_result(result, inp, "en")
        self.assertEqual(localized["evidence_role_code"], "R1")
        self.assertEqual(localized["evidence_role_name"], "Hypothesis generating")
        self.assertIn("outside the model's applicability domain", " ".join(localized["interpretations"]).lower())
        self.assertTrue(all(gap["title"] for gap in localized["data_gaps"]))
        self.assertTrue(any(gap["code"] == "ET-G006" for gap in localized["data_gaps"]))
        self.assertIn("evidence_confidence", localized)
        self.assertIn("prediction_reliability", localized)
        self.assertIn("toxicity_direction", localized)
        self.assertIn("development_concern", localized)
        self.assertIn("ai_credibility_profile", localized)


    def test_audit_localization(self) -> None:
        self.assertEqual(audit_action_label("EarlyTox 평가 실행", "en"), "EarlyTox assessment run")
        self.assertEqual(audit_detail_label("문서 2개, Assertion 5개", "en"), "2 document(s), 5 Assertion(s)")
        self.assertIn("Hypothesis generating", audit_detail_label("R1 - 가설 생성", "en"))

    def test_english_reports(self) -> None:
        inp = load_case("GP-L-CT — 적용범위 밖 음성예측", "en")
        result = evaluate(inp)
        markdown = build_markdown_report(inp, result, project_name="GP-L-CT", language="en")
        self.assertIn("Advisory Report", markdown)
        self.assertIn("Assessment Overview", markdown)
        self.assertIn("Hypothesis generating", markdown)
        self.assertIn("Are the current AI", markdown)
        pdf = build_pdf_report(inp, result, project_name="GP-L-CT", language="en")
        self.assertGreater(len(pdf), 5000)
        csv_bytes = build_gap_csv(result, inp, language="en")
        self.assertIn(b"Decision Impact", csv_bytes)


if __name__ == "__main__":
    unittest.main()
