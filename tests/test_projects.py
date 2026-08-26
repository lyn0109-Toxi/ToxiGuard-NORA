from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from nora.cases import gp_l_ct_case
from nora.projects import ProjectBundle, ProjectStore


class ProjectStoreTests(unittest.TestCase):
    def test_save_load_delete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = ProjectStore(Path(tmp) / "projects.db")
            project = ProjectBundle.new("GP-L-CT")
            project.assessment_input = gp_l_ct_case()
            store.save(project)
            loaded = store.load(project.project_id)
            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual(loaded.project_name, "GP-L-CT")
            self.assertEqual(loaded.assessment_input.product.product_name, "GP-L-CT")
            self.assertEqual(len(store.list_projects()), 1)
            store.delete(project.project_id)
            self.assertEqual(store.list_projects(), [])


if __name__ == "__main__":
    unittest.main()
