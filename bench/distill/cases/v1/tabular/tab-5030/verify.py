# DISTILL-CANARY-2a7e15b8 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["ledger_2026-08.csv"])))
charges = sum(float(r["amount"]) for r in rows if r["entry_type"] == "charge")
credits = sum(float(r["amount"]) for r in rows if r["entry_type"] == "credit")
print(json.dumps({"expected_number": round(charges - credits, 2)}))
