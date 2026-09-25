# DISTILL-CANARY-93e1c68d : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
panels = csv.DictReader(io.StringIO(case["files"]["pricing/panels-2026-09.csv"]))
price = next(r["list_price_gbp"] for r in panels if r["panel"] == "Aluminium shopfront")
terms = csv.DictReader(io.StringIO(case["files"]["pricing/trade-agreements.csv"]))
discount = next(r["discount_percent"] for r in terms if r["agreement"] == "Silver account")
total = float(price) * 4 * (100 - float(discount)) / 100
print(json.dumps({"expected_number": round(total, 2)}))
