# DISTILL-CANARY-761c1f70 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/receivables_2026-08.csv"])))
bal = sum(Decimal(r["应收"]) + Decimal(r["冲销"]) for r in rows)
print(json.dumps({"expected_number": float(bal)}))
