import json
import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class TestFlagshipClaimAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.claims = json.loads((ROOT/"data"/"flagship_claim_audit.json").read_text(encoding="utf-8"))
        cls.refs = json.loads((ROOT/"data"/"validated_reference_registry.json").read_text(encoding="utf-8"))

    def test_nine_cases_present(self):
        self.assertEqual(len({c["case_id"] for c in self.claims}), 9)

    def test_every_claim_has_corrected_wording(self):
        self.assertTrue(all(c["corrected_wording"].strip() for c in self.claims))

    def test_synthetic_claims_are_marked(self):
        rows = [c for c in self.claims if c["claim_type"]=="synthetic_assumption"]
        self.assertTrue(rows)
        self.assertTrue(all(c["verification_status"]=="SYNTHETIC" for c in rows))

    def test_tir202_emerging_claims_are_held(self):
        rows = {c["claim_id"]:c for c in self.claims}
        self.assertEqual(rows["TIR-202-C01"]["verification_status"], "HOLD")
        self.assertEqual(rows["TIR-202-C02"]["verification_status"], "HOLD")

    def test_phase2_does_not_prove_target_invalidity(self):
        row = next(c for c in self.claims if c["claim_id"]=="ASO-302-C04")
        self.assertEqual(row["verification_status"], "HOLD")

    def test_reference_ids_resolve(self):
        ids = {r["source_id"] for r in self.refs}
        self.assertTrue(all(s in ids for c in self.claims for s in c["source_ids"]))

    def test_validator(self):
        proc = subprocess.run([sys.executable, str(ROOT/"scripts"/"validate_flagship_claims.py")],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout+proc.stderr)

if __name__ == "__main__":
    unittest.main()
