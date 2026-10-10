# DISTILL-CANARY-e13c154d : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/orders_2026-09.csv"])))
n = sum(1 for r in rows if r["渠道"] == "团购")
print(json.dumps({"expected_number": float(n)}))
