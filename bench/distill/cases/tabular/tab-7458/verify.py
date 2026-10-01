# DISTILL-CANARY-d8fceb13 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/kiln_sales_2026-08.csv"])))
seen = set()
net = Decimal("0")
for r in rows:
    if r["单号"] in seen:
        continue
    seen.add(r["单号"])
    net += Decimal(r["金额"]) - Decimal(r["退款"])
print(json.dumps({"expected_number": float(net)}))
