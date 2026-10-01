# DISTILL-CANARY-4daaf5b9 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/loans_2026Q1.csv"]))
n = 0
for r in rows:
    if r["loan_month"] == "2026-03" and r["branch"] == "Milldale" and r["circ"] == "Y":
        n += 1
print(json.dumps({"expected_number": n}))
