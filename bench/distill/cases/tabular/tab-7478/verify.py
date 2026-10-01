# DISTILL-CANARY-e9c06122 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/deliveries_2026-08.csv"])))
fee = Decimal("0")
for r in rows:
    frozen = r["品类"] in ("冰皮", "慕斯")
    if not frozen and Decimal(r["金额"]) >= Decimal("88"):
        continue
    fee += Decimal("6")
print(json.dumps({"expected_number": float(fee)}))
