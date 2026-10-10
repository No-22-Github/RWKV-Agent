# DISTILL-CANARY-a061a202 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
fields = {}
for line in files["bookings/consignment_3382.txt"].splitlines():
    if " " in line:
        key, value = line.split(" ", 1)
        fields[key] = value
units = {}
for row in csv.reader(io.StringIO(files["standards/freight_units.csv"])):
    units[row[0]] = float(row[1])
print(json.dumps({
    "expected_number": float(fields["volume_cubic_feet"]) / units["measurement_ton_cubic_feet"]
}))
