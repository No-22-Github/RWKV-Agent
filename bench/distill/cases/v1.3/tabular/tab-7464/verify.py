# DISTILL-CANARY-b74b3187 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/tire_orders_2026-08.csv"])))
n = sum(1 for r in rows if r["客户"] == "望江轮胎")
print(json.dumps({"expected_number": float(n)}))
