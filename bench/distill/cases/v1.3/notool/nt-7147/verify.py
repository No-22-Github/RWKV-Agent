# DISTILL-CANARY-b276ffe0 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["training/runs.csv"]))
mi = next(float(r["distance_mi"]) for r in rows if r["run_date"] == "2026-09-13")
print(json.dumps({"expected_number": round(mi * 1.609344, 2)}))
