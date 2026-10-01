# DISTILL-CANARY-b0f027ec : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["stock/盘点-初盘.csv"]))
total = 0.0
for r in rows:
    total += float(r["数量"])
print(json.dumps({"expected_number": round(total, 2)}))
