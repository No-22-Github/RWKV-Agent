# DISTILL-CANARY-77357de9 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["kelp_landings_2026-08.csv"]))
print(json.dumps({"expected_number": round(sum(float(r["kelp_tonnes"]) for r in rows), 1)}))
