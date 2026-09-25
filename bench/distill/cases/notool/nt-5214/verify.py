# DISTILL-CANARY-a2c93e70 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = [r for r in csv.DictReader(io.StringIO(case["files"]["collections/band-prices-2026-09.csv"]))]
price = next(r["price_gbp"] for r in rows if float(r["up_to_kg"]) >= 3200)
print(json.dumps({"expected_number": float(price)}))
