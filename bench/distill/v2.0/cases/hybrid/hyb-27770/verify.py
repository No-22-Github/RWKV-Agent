# DISTILL-CANARY-60a2f1a0 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["sales/till-export-2026-09.csv"]))
total = 0.0
for r in rows:
    total += float(r["不含运费"])
print(json.dumps({"expected_number": round(total, 2)}))
