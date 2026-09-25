# DISTILL-CANARY-4c285423 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["vat_grading_2026-07.csv"])))
declared = sum(float(r["declared_kg"]) for r in rows)
graded = sum(float(r["graded_kg"]) for r in rows)
print(json.dumps({"expected_number": round(declared - graded, 1)}))
