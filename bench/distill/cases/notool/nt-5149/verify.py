# DISTILL-CANARY-67e6196e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
fields = {}
for line in files["jobs/banner_docket_2471.txt"].splitlines():
    if " " in line:
        key, value = line.split(" ", 1)
        fields[key] = value
units = {}
for row in csv.reader(io.StringIO(files["standards/typesetting_units.csv"])):
    units[row[0]] = float(row[1])
print(json.dumps({
    "expected_number": float(fields["depth_points"]) / units["inch_to_point"]
}))
