# DISTILL-CANARY-0693b186 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
charges = list(csv.DictReader(io.StringIO(files["chillers/charge_sheet_9241.tsv"]), delimiter="\t"))
gallons = float(next(row["charge_imperial_gallons"] for row in charges if row["circuit"] == "primary"))
units = {}
for row in csv.reader(io.StringIO(files["standards/coolant_units.csv"])):
    units[row[0]] = float(row[1])
print(json.dumps({
    "expected_number": gallons * units["imperial_gallon_to_fluid_ounce"]
}))
