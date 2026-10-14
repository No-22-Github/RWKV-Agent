# DISTILL-CANARY-30f3cc4f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["collections_2026-09.csv"])))
net = sum(int(r["gross_kg"]) - int(r["returns_kg"]) for r in rows)
print(json.dumps({"expected_number": net}))
