# DISTILL-CANARY-698561b5 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["intake/grape_intake_2026-09.csv"])))
total = sum(int(r["weight_kg"]) for r in rows if r["variety"] == "Merlot")
print(json.dumps({"expected_number": total}))
