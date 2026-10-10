# DISTILL-CANARY-96223a0c : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["logs/refunds.csv"]))
total = 0.0
for r in rows:
    if r["reason"] == "defective" and r["date"].startswith("2026-08"):
        total += float(r["amount_usd"])
print(json.dumps({"expected_number": round(total, 2)}))
