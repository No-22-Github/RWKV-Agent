# DISTILL-CANARY-d3b8f019 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["picking_log_2026.csv"])))
earlier = [r for r in rows if r["pick_month"] == "2025-08"]
later = [r for r in rows if r["pick_month"] == "2026-08"]
if not earlier:
    print(json.dumps({"expected_string": "UNKNOWN"}))
else:
    old = sum(float(r["weight_kg"]) for r in earlier)
    new = sum(float(r["weight_kg"]) for r in later)
    print(json.dumps({"expected_number": round((new - old) / old * 100, 1)}))
