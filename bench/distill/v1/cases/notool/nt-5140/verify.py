# DISTILL-CANARY-b5220c6c : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
fields = {}
for line in files["plants/steam_meter_2946.txt"].splitlines():
    if " " in line:
        key, value = line.split(" ", 1)
        fields[key] = value
equivalents = {}
for row in csv.reader(io.StringIO(files["standards/heat_equivalents.csv"])):
    equivalents[row[0]] = float(row[1])
print(json.dumps({
    "expected_number": float(fields["steam_gigajoules"]) / equivalents["kilowatt_hour_to_gigajoule"]
}))
