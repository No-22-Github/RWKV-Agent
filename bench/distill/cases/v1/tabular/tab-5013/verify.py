# DISTILL-CANARY-9e50c6b3 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["ledger_2026-08.csv"])))
charged = sum(float(r["charge"]) for r in rows)
refunded = sum(float(r["refund"]) for r in rows)
print(json.dumps({"expected_number": round(charged - refunded, 2)}))
