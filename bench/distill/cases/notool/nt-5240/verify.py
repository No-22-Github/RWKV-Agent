# DISTILL-CANARY-9ac6788a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rates = {}
for row in csv.reader(io.StringIO(files["standards/barrel_units.csv"])):
    rates[row[0]] = float(row[1])
discharge = json.loads(files["discharges/tanker_8825.json"])
print(json.dumps({
    "expected_number": discharge["barrels_landed"] * rates["us_gallon_per_barrel"]
}))
