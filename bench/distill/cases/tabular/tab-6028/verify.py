# DISTILL-CANARY-f8f15e1e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
orders = list(csv.DictReader(io.StringIO(case["files"]["orders/orders_2026-08.csv"])))
refunds = list(csv.DictReader(io.StringIO(case["files"]["refunds/refunds_2026-08.csv"])))
net = sum(float(r["amount"]) for r in orders) + sum(float(r["amount"]) for r in refunds)
print(json.dumps({"expected_number": round(net, 2)}))
