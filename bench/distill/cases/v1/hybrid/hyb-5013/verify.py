# DISTILL-CANARY-b3e06d18 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["orders/hesketh-order.csv"]))
units = sum(int(row["ordered"]) - int(row["delivered"]) for row in rows)
print(json.dumps({"expected_number": units}))
