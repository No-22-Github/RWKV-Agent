# DISTILL-CANARY-aaa849f1 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/settlement_2026-08.csv"])))
net = sum(Decimal(r["运费"]) - Decimal(r["扣款"]) for r in rows)
print(json.dumps({"expected_number": float(net)}))
