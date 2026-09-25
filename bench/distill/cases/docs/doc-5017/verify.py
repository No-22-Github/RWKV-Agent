# DISTILL-CANARY-f4c60a19 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
charges = case["files"]["fees/charges.csv"]
rows = list(csv.DictReader(io.StringIO(charges)))

ASKED = "wardrobe box hire each"
value = None
for row in rows:
    if row["service"].strip().lower() == ASKED:
        value = float(row["charge_gbp"])

print(json.dumps({"expected_number": value}))
