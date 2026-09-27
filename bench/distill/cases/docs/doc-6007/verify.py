# DISTILL-CANARY-757dc115 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["handbook/entitlements.csv"]))

# README.md: one row per entitlement, and the row names the staff group it
# applies to.
value = None
for row in rows:
    if row["entitlement"].strip().lower() == "study leave - laboratory technician":
        value = float(row["days"])
        break

print(json.dumps({"expected_number": value}))
