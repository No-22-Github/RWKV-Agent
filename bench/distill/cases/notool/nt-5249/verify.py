# DISTILL-CANARY-ad748e82 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
units = {}
for row in csv.reader(io.StringIO(files["standards/energy_units.csv"])):
    units[row[0]] = float(row[1])
record = {}
for line in files["returns/yield_return_6241.txt"].splitlines():
    parts = line.split()
    if len(parts) == 2:
        record[parts[0]] = parts[1]
print(json.dumps({
    "expected_number": float(record["generation_kilowatt_hours"]) * units["megajoule_per_kilowatt_hour"]
}))
