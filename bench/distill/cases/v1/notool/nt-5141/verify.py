# DISTILL-CANARY-659c747c : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
tests = list(csv.DictReader(io.StringIO(files["sites/pump_test_4271.tsv"]), delimiter="\t"))
duty = float(next(row["duty_litres_per_second"] for row in tests if row["pump"] == "P3"))
units = {}
for row in csv.reader(io.StringIO(files["standards/flow_units.csv"])):
    units[row[0]] = float(row[1])
print(json.dumps({
    "expected_number": duty * units["litre_per_second_to_cubic_metre_per_hour"]
}))
