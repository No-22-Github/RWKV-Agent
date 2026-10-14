# DISTILL-CANARY-5de89e7b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["tests/pace_2026-09.csv"]))
pace = next(float(r["pace_min_per_km"]) for r in rows if r["member"] == "周航")
print(json.dumps({"expected_number": round(60 / pace, 2)}))
