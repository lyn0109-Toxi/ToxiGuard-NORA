#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = json.loads((ROOT / "data" / "flagship_claim_audit.json").read_text(encoding="utf-8"))
REFS = json.loads((ROOT / "data" / "validated_reference_registry.json").read_text(encoding="utf-8"))
ref_ids = {x["source_id"] for x in REFS}

errors = []
required_cases = {
    "TAC-101","TAC-102","TAC-103",
    "TIR-201","TIR-202","TIR-203",
    "ASO-301","ASO-302","ASO-303"
}
seen_cases = {x["case_id"] for x in CLAIMS}
if seen_cases != required_cases:
    errors.append(f"case mismatch: missing={required_cases-seen_cases}, extra={seen_cases-required_cases}")

claim_ids = [x["claim_id"] for x in CLAIMS]
if len(claim_ids) != len(set(claim_ids)):
    errors.append("duplicate claim_id")

for c in CLAIMS:
    ctype = c["claim_type"]
    status = c["verification_status"]
    sources = c["source_ids"]
    if ctype in {"verified_fact","verified_with_limits","contextual_evidence"} and not sources:
        errors.append(f"{c['claim_id']}: evidence claim without source")
    for sid in sources:
        if sid not in ref_ids:
            errors.append(f"{c['claim_id']}: unknown source {sid}")
    if ctype == "synthetic_assumption" and status != "SYNTHETIC":
        errors.append(f"{c['claim_id']}: synthetic claim not marked SYNTHETIC")
    if status == "HOLD" and c["evidence_grade"] in {"A1","A2"}:
        errors.append(f"{c['claim_id']}: HOLD claim cannot carry A-grade without explanation")
    if not c["corrected_wording"].strip():
        errors.append(f"{c['claim_id']}: missing corrected wording")
    if not c["applicability_limits"].strip():
        errors.append(f"{c['claim_id']}: missing applicability limits")
    if c["severity"] == "critical" and not c["required_action"].strip():
        errors.append(f"{c['claim_id']}: critical claim missing action")

# Critical control: emerging tirzepatide/B12 claims must remain HOLD.
for cid in ("TIR-202-C01","TIR-202-C02"):
    row = next(x for x in CLAIMS if x["claim_id"] == cid)
    if row["verification_status"] != "HOLD":
        errors.append(f"{cid}: emerging analytical claim must remain HOLD")

# Critical control: randomized LY2181308 claim cannot claim target invalidity.
target_invalid = next(x for x in CLAIMS if x["claim_id"] == "ASO-302-C04")
if target_invalid["verification_status"] != "HOLD":
    errors.append("ASO-302-C04 causal overreach must remain HOLD")

if errors:
    print("FLAGSHIP CLAIM AUDIT: FAIL")
    for e in errors:
        print(" -", e)
    raise SystemExit(1)

print(f"FLAGSHIP CLAIM AUDIT: PASS ({len(CLAIMS)} claims, {len(REFS)} references)")
