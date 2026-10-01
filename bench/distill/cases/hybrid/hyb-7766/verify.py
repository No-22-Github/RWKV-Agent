# DISTILL-CANARY-56ba9c55 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["sales/专柜零售-2026-09.csv"]))
total = 0.0
for r in rows:
    total += float(r["金额"])
print(json.dumps({"expected_number": round(total, 2)}))
