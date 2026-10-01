# DISTILL-CANARY-d6e5bf3c : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["logs/deliveries.csv"]))
total = 0.0
for r in rows:
    if r["supplier"] == "Oatfield Dairy" and r["date"].startswith("2026-08"):
        total += float(r["total_gbp"])
print(json.dumps({"expected_number": round(total, 2)}))
