# DISTILL-CANARY-d9b2660a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["turf_cutting_2026-05.csv"]))
turfs = sum(int(r["turf_count"]) for r in rows)
print(json.dumps({"expected_number": round(1.85 * turfs, 2)}))
