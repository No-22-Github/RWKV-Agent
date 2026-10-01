# DISTILL-CANARY-7dfb1b6e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["patrol/route_2026w40.csv"]))
total_km = sum(float(r["长度公里"]) for r in rows)
value = total_km * 1000
print(json.dumps({"expected_number": value}))
