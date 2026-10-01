# DISTILL-CANARY-e7faa8da : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
led = csv.DictReader(io.StringIO(case["files"]["data/ledger_2026-09.csv"]))
bank = csv.DictReader(io.StringIO(case["files"]["data/bank_2026-09.csv"]))
a = sum((Decimal(r["不含税金额"]) for r in led if r["月份"] == "2026-09"), Decimal("0"))
b = sum((Decimal(r["金额"]) for r in bank if r["记账月份"] == "2026-09"), Decimal("0"))
print(json.dumps({"expected_number": float(a - b)}))
