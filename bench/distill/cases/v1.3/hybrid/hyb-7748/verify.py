# DISTILL-CANARY-b8fc75ff : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["purchases/采购流水.csv"]))
total = 0.0
for r in rows:
    if r["供应商"] == "维庚建材" and r["日期"].startswith("2026-08"):
        total += float(r["金额"])
print(json.dumps({"expected_number": round(total, 2)}))
