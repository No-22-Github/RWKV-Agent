# DISTILL-CANARY-2966f826 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["ledger/aging-2026-09.csv"]))
owed = next(r["outstanding_gbp"] for r in rows if r["account"] == "Harlow Bay Marine")
print(json.dumps({"expected_number": float(owed)}))
