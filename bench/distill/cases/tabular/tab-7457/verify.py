# DISTILL-CANARY-83c46011 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/store_settlement_2026-09.csv"])))
total = sum(Decimal(r["实收金额"]) for r in rows)
print(json.dumps({"expected_number": float(total)}))
