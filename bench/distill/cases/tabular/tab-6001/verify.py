# DISTILL-CANARY-53d53c6a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["ledger/sales_2026-07.csv"])))
total = sum(float(r["revenue"]) for r in rows)
print(json.dumps({"expected_number": round(total, 2)}))
