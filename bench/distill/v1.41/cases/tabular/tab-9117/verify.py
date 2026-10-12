# DISTILL-CANARY-323ae948 : distillation case
import json
case = json.load(open("case.json"))
rows = dict(r.split(",") for r in case["files"]["data/prices.csv"].splitlines()[1:])
assert rows["K-208"] == "38.40" and rows["K-2080"] == "41.00"
assert case["files"]["data/prices-2025.csv"].splitlines()[0] == "sku,unit_price" and "K-208,35.00" in case["files"]["data/prices-2025.csv"]
print(json.dumps({"expected_contains_any": [rows["K-208"]]}))
