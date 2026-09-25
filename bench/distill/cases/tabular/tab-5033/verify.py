# DISTILL-CANARY-a80d47c6 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["deliveries_2026-08.csv"])))
prices = {r["coal_grade"]: float(r["price_per_tonne"])
          for r in csv.DictReader(io.StringIO(case["files"]["grade_prices.csv"]))}
seen = set()
total = 0.0
for row in rows:
    if row["customer"] != "Cawdor Brickworks" or row["delivery_id"] in seen:
        continue
    seen.add(row["delivery_id"])
    total += float(row["tonnes"]) * prices[row["coal_grade"]]
print(json.dumps({"expected_number": round(total, 2)}))
