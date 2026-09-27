# DISTILL-CANARY-1274cc09 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["terms/booking-terms.csv"]))

# README.md: each row carries one term, its amount and the unit the amount
# is counted in.
value = None
for row in rows:
    if row["item"].strip().lower() == "balance payment before arrival":
        value = float(row["amount"])
        break

print(json.dumps({"expected_number": value}))
