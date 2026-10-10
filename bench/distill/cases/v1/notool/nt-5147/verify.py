# DISTILL-CANARY-7563b1fd : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
fields = {}
for line in files["panels/station_address_3318.txt"].splitlines():
    if " " in line:
        key, value = line.split(" ", 1)
        fields[key] = value
switch = fields["switch_bank"].strip()
# the sheet is written from bit 7 down to bit 0, the order the bank reads in
weights = [int(row[1]) for row in csv.reader(io.StringIO(files["standards/bit_weights.csv"]))]
total = sum(weight for digit, weight in zip(switch, weights) if digit == "1")
print(json.dumps({"expected_number": total}))
