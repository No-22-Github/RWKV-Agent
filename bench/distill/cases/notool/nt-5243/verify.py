# DISTILL-CANARY-d34775b6 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rates = {}
for row in csv.reader(io.StringIO(files["standards/pressure_units.csv"])):
    rates[row[0]] = float(row[1])
record = {}
for line in files["tests/strength_test_3341.txt"].splitlines():
    parts = line.split()
    if len(parts) == 2:
        record[parts[0]] = parts[1]
print(json.dumps({
    "expected_number": float(record["gauge_kilopascals"]) / rates["kilopascal_per_bar"]
}))
