# DISTILL-CANARY-c74e6b10 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["billing/payments_june.csv"]))
totals = {}
for r in rows:
    tier = r["membership_tier"]
    totals[tier] = totals.get(tier, Decimal("0")) + Decimal(r["amount_due"])
print(json.dumps({"expected_number": float(max(totals.values()))}))
