# DISTILL-CANARY-2f80632f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["terms/booking-terms.csv"])))

# README.md: terms that are not on the sheet are settled directly with the
# house manager, so the sheet is the complete list of standing terms.
value = "UNKNOWN"
for row in rows:
    if "pet" in row["item"].strip().lower():
        value = row["amount"].strip()
        break

print(json.dumps({"expected_string": value}))
