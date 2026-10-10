# DISTILL-CANARY-99c9395d : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/rentals_log.csv"]))
total = Decimal("0")
for r in rows:
    if r["rental_month"] == "2026-07" and r["rental_class"] == "Sunset Paddle":
        total += Decimal(r["revenue"])
print(json.dumps({"expected_number": float(total)}))
