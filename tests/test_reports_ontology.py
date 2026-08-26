from __future__ import annotations

import unittest
from pathlib import Path

from rdflib import Graph

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
        pdf = build_pdf_report(inp, result, project_name="GP-L-CT")
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertGreater(len(pdf), 3000)
        self.assertEqual(pdf, build_pdf_report(inp, result, project_name="GP-L-CT"))
        jsonld = build_jsonld(inp, result, project_name="GP-L-CT")
        self.assertIn("@context", jsonld)
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
