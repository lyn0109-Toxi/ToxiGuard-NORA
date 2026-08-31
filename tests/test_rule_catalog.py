from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RuleCatalogTests(unittest.TestCase):
    def test_rule_catalog_contract(self) -> None:
        rows = json.loads((ROOT / "data" / "rule_catalog.json").read_text(encoding="utf-8"))
        self.assertIsInstance(rows, list)
        self.assertGreaterEqual(len(rows), 10)
        required = {"rule_id", "name_ko", "condition", "conclusion", "maximum_role"}
        ids: list[str] = []
        for row in rows:
            self.assertTrue(required <= set(row))
            self.assertRegex(row["rule_id"], r"^ET-R\d{3}$")
            self.assertRegex(row["maximum_role"], r"^R[0-5](?:-R[0-5])?$")
            ids.append(row["rule_id"])
        self.assertEqual(len(ids), len(set(ids)))

    def test_ai_credibility_rule_catalog_contract(self) -> None:
        rows = json.loads((ROOT / "data" / "ai_credibility_rule_catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 15)
        required = {"rule_id", "name_ko", "name_en", "condition", "condition_en", "conclusion", "conclusion_en", "maximum_role"}
        ids: list[str] = []
        for row in rows:
            self.assertTrue(required <= set(row))
            self.assertRegex(row["rule_id"], r"^AI-R\d{3}$")
            self.assertRegex(row["maximum_role"], r"^R[0-5](?:-R[0-5])?$")
            ids.append(row["rule_id"])
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
