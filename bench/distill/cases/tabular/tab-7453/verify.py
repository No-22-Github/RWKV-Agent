# DISTILL-CANARY-061a4168 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/drygoods_orders_2026-04.csv"])))
total = sum(Decimal(r["金额"]) for r in rows)
avg = (total / len(rows)).quantize(Decimal("0.01"))
print(json.dumps({"expected_number": float(avg)}))
