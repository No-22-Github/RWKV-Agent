# DISTILL-CANARY-2b81f9d3 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
charges = case["files"]["fees/charges.csv"]
rows = list(csv.DictReader(io.StringIO(charges)))

# README.md: the sheet lists the firm's standard charges, and work it does not
# list is quoted by the office after a survey. Taking a fitted wardrobe down and
# putting it back together is not one of the listed services.
ASKED = "fitted wardrobe disassembly and reassembly"
value = "UNKNOWN"
for row in rows:
    if row["service"].strip().lower() == ASKED:
        value = row["charge_gbp"].strip()

print(json.dumps({"expected_string": value}))
