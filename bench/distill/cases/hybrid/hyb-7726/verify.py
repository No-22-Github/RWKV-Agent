# DISTILL-CANARY-9c41e2a7 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["exports/august_orders.csv"]))
count = sum(1 for r in rows if r["channel"] == "直营" and r["date"].startswith("2026-08"))
print(json.dumps({"expected_number": count}))
