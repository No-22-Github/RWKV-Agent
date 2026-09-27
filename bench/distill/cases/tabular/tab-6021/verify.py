# DISTILL-CANARY-41553a1e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["trade_sales/orders_2026-08.csv"])))
per = {}
for r in rows:
    per[r["client"]] = per.get(r["client"], 0.0) + float(r["amount"])
ranked = sorted(per.values(), reverse=True)
print(json.dumps({"expected_number": round(ranked[1], 2)}))
