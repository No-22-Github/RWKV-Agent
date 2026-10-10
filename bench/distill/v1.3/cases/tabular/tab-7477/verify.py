# DISTILL-CANARY-4963224a : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/sales_2026-09.csv"])))
total = sum(Decimal(r["金额"]) for r in rows)
comm = total * Decimal("0.03")
print(json.dumps({"expected_number": float(comm)}))
