# DISTILL-CANARY-58d2e907 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/maintenance_log.csv"]))
costs = [
    Decimal(r["作业费用"])
    for r in rows
    if r["作业类型"] == "修剪" and r["作业月份"] == "2026-08"
]
print(json.dumps({"expected_number": float(sum(costs) / len(costs))}))
