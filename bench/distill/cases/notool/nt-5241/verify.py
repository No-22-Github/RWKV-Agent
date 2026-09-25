# DISTILL-CANARY-a3648a0f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rates = {}
for row in csv.reader(io.StringIO(files["standards/charge_units.csv"])):
    rates[row[0]] = float(row[1])
record = {}
for line in files["tests/battery_test_7308.txt"].splitlines():
    parts = line.split()
    if len(parts) == 2:
        record[parts[0]] = parts[1]
print(json.dumps({
    "expected_number": float(record["capacity_ampere_hours"]) * rates["coulomb_per_ampere_hour"]
}))
