# DISTILL-CANARY-5a6517ca : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/repairs_2026-09.csv"])))
net = sum(Decimal(r["工时费"]) - Decimal(r["积分抵扣"]) for r in rows)
print(json.dumps({"expected_number": float(net)}))
