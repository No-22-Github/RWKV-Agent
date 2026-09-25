# DISTILL-CANARY-b7d2148e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["tank_usage_2026-08.csv"])))
rates = [float(r["used_litres"]) / float(r["capacity_litres"]) for r in rows]
print(json.dumps({"expected_number": round(max(rates) * 100, 1)}))
