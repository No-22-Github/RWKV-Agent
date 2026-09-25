# DISTILL-CANARY-64f0a1c7 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["pricing/hoarding-2026-09.csv"]))
rate = next(r["per_week_gbp"] for r in rows if r["panel_length_m"] == "36")
total = float(rate) * 9
print(json.dumps({"expected_number": round(total, 2)}))
