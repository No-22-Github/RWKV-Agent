# DISTILL-CANARY-b9634f2d : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["coatings/schedule-2026-09.csv"]))
rate = next(r["per_sqm_gbp"] for r in rows if r["finish"] == "Powder coat")
total = float(rate) * 40
print(json.dumps({"expected_number": round(total, 2)}))
