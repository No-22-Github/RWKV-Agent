# DISTILL-CANARY-2e85667d : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/orders_2026-08.csv"])))
custs = {r["客户"] for r in rows if r["客户类型"] == "单位"}
print(json.dumps({"expected_number": float(len(custs))}))
