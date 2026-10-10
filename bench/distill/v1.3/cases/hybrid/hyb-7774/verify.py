# DISTILL-CANARY-58a3749a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["bills/freight-bills-2026-08.csv"]))
total = 0.0
for r in rows:
    total += float(r["billed_weight_kg"])
print(json.dumps({"expected_number": round(total, 2)}))
