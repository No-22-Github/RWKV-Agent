# DISTILL-CANARY-6a50c36f : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/intake_2026-09.csv"])))
total = sum(Decimal(r["吨位"]) for r in rows if r["记录类型"] == "明细")
print(json.dumps({"expected_number": float(total)}))
