# DISTILL-CANARY-8a63f2b5 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["logs/intake_september.csv"]))
count = sum(1 for r in rows
            if r["process"] == "C-41" and r["intake_date"] == "2026-09-12")
print(json.dumps({"expected_number": count}))
