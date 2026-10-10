# DISTILL-CANARY-3b38152d : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["tills/till-export-2026-08.csv"]))
total = 0.0
for r in rows:
    total += float(r["net_gbp"])
print(json.dumps({"expected_number": round(total, 2)}))
