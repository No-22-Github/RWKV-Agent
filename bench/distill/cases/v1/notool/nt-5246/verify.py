# DISTILL-CANARY-c4b5727b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rates = {}
for row in csv.reader(io.StringIO(files["standards/frequency_units.csv"])):
    rates[row[0]] = float(row[1])
record = {}
for line in files["tests/overspeed_trip_5540.txt"].splitlines():
    parts = line.split()
    if len(parts) == 2:
        record[parts[0]] = parts[1]
print(json.dumps({
    "expected_number": float(record["full_load_revolutions_per_minute"]) / rates["revolution_per_minute_per_hertz"]
}))
