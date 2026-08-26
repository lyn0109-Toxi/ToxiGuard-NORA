from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RepositoryContractTests(unittest.TestCase):
    def test_version_metadata_matches(self) -> None:
        package_text = (ROOT / "nora" / "__init__.py").read_text(encoding="utf-8")
        package_version = re.search(r'__version__\s*=\s*"([^"]+)"', package_text).group(1)
        self.assertEqual((ROOT / "VERSION").read_text(encoding="utf-8").strip(), package_version)
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn(f'version = "{package_version}"', pyproject)

    def test_public_site_contract(self) -> None:
        ontology = json.loads((ROOT / "site" / "data" / "ontology.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(ontology["modules"]), 15)
        self.assertGreaterEqual(len(ontology["chain"]), 12)
        self.assertEqual(len(ontology["roles"]), 6)
        html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        self.assertIn("styles.css", html)
        self.assertIn("app.js", html)

    def test_golden_case_artifacts_match_current_versions(self) -> None:
        expected_roles = {
            "gp_l_ct": "R1",
            "concordant": "R4",
            "conflict": "R2",
        }
        package_text = (ROOT / "nora" / "__init__.py").read_text(encoding="utf-8")
        ontology_version = re.search(r'__ontology_version__\s*=\s*"([^"]+)"', package_text).group(1)
        rule_set_version = re.search(r'__rule_set_version__\s*=\s*"([^"]+)"', package_text).group(1)
        project_schema = re.search(r'__project_schema_version__\s*=\s*"([^"]+)"', package_text).group(1)
        for case_name, expected_role in expected_roles.items():
            project = json.loads((ROOT / "samples" / case_name / "project.nora.json").read_text(encoding="utf-8"))
            self.assertEqual(project["schema_version"], project_schema)
            self.assertEqual(project["last_result"]["evidence_role_code"], expected_role)
            self.assertEqual(project["last_result"]["audit"]["ontology_version"], ontology_version)
            self.assertEqual(project["last_result"]["audit"]["rule_set_version"], rule_set_version)


if __name__ == "__main__":
    unittest.main()
