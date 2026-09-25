# DISTILL-CANARY-46cf80a1 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["rates/carer-grades-2026-09.csv"]))
rate = next(r["hourly_gbp"] for r in rows if r["grade"] == "Senior carer")
total = float(rate) * 8
print(json.dumps({"expected_number": round(total, 2)}))
