# DISTILL-CANARY-3f15fb2c : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/rice_intake_sept.csv"])))
tons = sum(Decimal(r["吨位"]) for r in rows)
fee = tons * Decimal("4.50")
print(json.dumps({"expected_number": float(fee)}))
