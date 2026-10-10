# DISTILL-CANARY-3210d48a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["logs/freight-invoices.csv"]))
total = 0.0
for r in rows:
    if r["date"].startswith("2026-08") and float(r["cost_usd"]) > 1300:
        total += float(r["cost_usd"])
print(json.dumps({"expected_number": round(total, 2)}))
