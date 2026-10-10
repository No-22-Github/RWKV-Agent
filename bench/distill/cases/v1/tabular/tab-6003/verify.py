# DISTILL-CANARY-15e3253b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["kiln/loads_2026-08.csv"])))
weights = [float(r["weight_kg"]) for r in rows]
print(json.dumps({"expected_number": round(sum(weights) / len(weights), 2)}))
