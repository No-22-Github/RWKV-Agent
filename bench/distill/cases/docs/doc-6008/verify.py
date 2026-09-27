# DISTILL-CANARY-4eb0b018 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["handbook/entitlements.csv"])))

# README.md: the handbook grants exactly what the table lists; anything
# beyond it is agreed case by case with a director.
value = "UNKNOWN"
for row in rows:
    if "sabbatical" in row["entitlement"].strip().lower():
        value = row["days"].strip()
        break

print(json.dumps({"expected_string": value}))
