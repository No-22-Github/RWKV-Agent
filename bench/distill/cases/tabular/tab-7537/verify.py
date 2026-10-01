# DISTILL-CANARY-44f91dd1 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/reports_2026-08.csv"])))
sel = [Decimal(r["bill_gbp"]) for r in rows
       if r["report_month"] == "2026-08" and r["plan"] == "Corporate Standard"]
avg = sum(sel) / len(sel)
print(json.dumps({"expected_number": float(avg)}))
