# DISTILL-CANARY-1e9d54b3 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["rates/machine-rates-2026-09.csv"]))
rate = next(r["per_day_gbp"] for r in rows if r["platform_height_m"] == "16")
total = float(rate) * 4
print(json.dumps({"expected_number": round(total, 2)}))
