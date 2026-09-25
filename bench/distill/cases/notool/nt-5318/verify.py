# DISTILL-CANARY-2a75b0e9 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["pricing/carriage-2026-09.csv"]))
rate = next(r["per_cylinder_gbp"] for r in rows if r["term"] == "Depot collection")
total = float(rate) * 24
print(json.dumps({"expected_number": round(total, 2)}))
