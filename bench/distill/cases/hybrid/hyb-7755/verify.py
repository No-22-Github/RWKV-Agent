# DISTILL-CANARY-2170d83b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["usage/api-usage.csv"]))
total = 0.0
for r in rows:
    if r["tenant"] == "meridian-health":
        total += float(r["overage_usd"])
print(json.dumps({"expected_number": round(total, 2)}))
