# DISTILL-CANARY-13baf2ae : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["stock/food_inventory.csv"]))
kg = next(float(r["net_weight_kg"]) for r in rows if r["item"] == "成猫粮鸡肉味")
print(json.dumps({"expected_number": round(kg * 1000 / 50, 2)}))
