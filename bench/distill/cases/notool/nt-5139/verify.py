# DISTILL-CANARY-9dc9d703 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
runs = list(csv.DictReader(io.StringIO(files["contracts/marking_run_5518.tsv"]), delimiter="\t"))
miles = float(next(row["length_miles"] for row in runs if row["job"] == "LH-5518"))
units = {}
for row in csv.reader(io.StringIO(files["standards/length_units.csv"])):
    units[row[0]] = float(row[1])
print(json.dumps({"expected_number": miles * units["mile_to_yard"]}))
