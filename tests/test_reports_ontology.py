from __future__ import annotations

import unittest
from io import BytesIO
from pathlib import Path

from rdflib import Graph
from pypdf import PdfReader

from nora.cases import gp_l_ct_case
from nora.engine import evaluate
from nora.ontology import build_jsonld, build_turtle
from nora.reports import build_markdown_report, build_pdf_report


ROOT = Path(__file__).resolve().parents[1]


class ReportOntologyTests(unittest.TestCase):
    def test_markdown_pdf_and_jsonld(self) -> None:
        inp = gp_l_ct_case()
        result = evaluate(inp)
        markdown = build_markdown_report(inp, result, project_name="GP-L-CT")
        self.assertIn("ToxiGuard NORA EarlyTox", markdown)
        self.assertIn(result.evidence_role_code, markdown)
        self.assertIn("AI 독성 신뢰성 프로파일", markdown)
        self.assertIn("근거 신뢰도", markdown)
        self.assertIn("개발 우려", markdown)
        pdf = build_pdf_report(inp, result, project_name="GP-L-CT")
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertGreater(len(pdf), 3000)
        self.assertEqual(pdf, build_pdf_report(inp, result, project_name="GP-L-CT"))
        extracted_ko = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(pdf)).pages)
        self.assertIn("현재 AI와 사람 기반 NAM", extracted_ko)
        self.assertIn("0.0", extracted_ko)
        pdf_en = build_pdf_report(inp, result, project_name="GP-L-CT", language="en")
        extracted_en = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(pdf_en)).pages)
        self.assertIn("AI Toxicity Credibility Profile", extracted_en)
        self.assertIn("Hypothesis generating", extracted_en)
        jsonld = build_jsonld(inp, result, project_name="GP-L-CT")
        self.assertIn("@context", jsonld)
        self.assertIn("assessment:hasDevelopmentConcern", jsonld["assessment:hasAssessmentResult"])
        self.assertIn("ai:hasLeakageAssessment", jsonld["assessment:usesAIModelCard"])
        self.assertIn("ai:hasProbabilityType", jsonld["assessment:usesAIModelCard"])
        turtle = build_turtle(inp, result, project_name="GP-L-CT")
        graph = Graph()
        graph.parse(data=turtle, format="turtle")
        self.assertGreater(len(graph), 10)

    def test_static_ontology_parses(self) -> None:
        graph = Graph()
        graph.parse(ROOT / "ontology" / "tg_pto_et_core.ttl", format="turtle")
        self.assertGreater(len(graph), 10)
        shapes = Graph()
        shapes.parse(ROOT / "ontology" / "tg_pto_et_shapes.ttl", format="turtle")
        self.assertGreater(len(shapes), 5)


if __name__ == "__main__":
    unittest.main()
