# DISTILL-CANARY-0ad7b9e4 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/group_orders_2026-09.csv"])))
total = sum(Decimal(r["金额"]) for r in rows if r["渠道"] == "门店" and r["状态"] == "已完成")
print(json.dumps({"expected_number": float(total)}))
