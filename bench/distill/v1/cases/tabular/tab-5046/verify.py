# DISTILL-CANARY-ff09cb3b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["order_lines_2026-08.csv"])))
prices = {r["product_code"]: float(r["price_per_pack"])
          for r in csv.DictReader(io.StringIO(case["files"]["pack_prices.csv"]))}
value = sum(int(r["packs"]) * prices[r["product_code"]]
            for r in rows if r["customer"] == "Marlpit Nurseries")
print(json.dumps({"expected_number": round(value, 2)}))
