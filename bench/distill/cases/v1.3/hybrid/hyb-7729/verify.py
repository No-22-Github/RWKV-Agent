# DISTILL-CANARY-a2d60b83 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["orders/june_orders.csv"]))
count = sum(1 for r in rows if r["occasion"] == "wedding" and r["date"].startswith("2026-06"))
print(json.dumps({"expected_number": count}))
