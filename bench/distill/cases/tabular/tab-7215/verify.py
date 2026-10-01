# DISTILL-CANARY-6ec58d91 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/parking-2026-09.csv"]))
total = Decimal("0")
n = 0
for r in rows:
    if r["entry_date"] == "2026-09-17" and r["site"] == "Riverside Multi-Storey":
        total += Decimal(r["amount_gbp"])
        n += 1
if n < 1:
    raise SystemExit("fixture guard failed: the target rows are gone")
print(json.dumps({"expected_number": float(total)}))
