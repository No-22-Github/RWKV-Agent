# DISTILL-CANARY-ea4d0494 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/refills_2026-09.csv"]))
pats = set()
for r in rows:
    if r["refill_month"] == "2026-09" and r["channel"] == "Auto-Refill":
        pats.add(r["patient_code"])
print(json.dumps({"expected_number": len(pats)}))
