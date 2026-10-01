# DISTILL-CANARY-5980a914 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["sales/批发流水.csv"]))
total = 0.0
for r in rows:
    if r["日期"].startswith("2026-08"):
        total += float(r["金额"])
print(json.dumps({"expected_number": round(total * 20.5, 2)}))
