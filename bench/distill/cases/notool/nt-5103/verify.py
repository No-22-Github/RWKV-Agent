# DISTILL-CANARY-5152bb34 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["price-lists/retail-2026-09.csv"]))
price = next(r["price_gbp"] for r in rows if r["item_code"] == "DR-500")
print(json.dumps({"expected_number": float(price)}))
