# DISTILL-CANARY-d4c2cbc7 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
fields = {}
for line in files["ovens/bake_profile_7412.txt"].splitlines():
    if " " in line:
        key, value = line.split(" ", 1)
        fields[key] = value
factors = {}
for row in csv.reader(io.StringIO(files["standards/scale_factors.csv"])):
    factors[row[0]] = float(row[1])
print(json.dumps({
    "expected_number": float(fields["profile_celsius"]) * factors["celsius_multiplier"]
    + factors["fahrenheit_offset"]
}))
