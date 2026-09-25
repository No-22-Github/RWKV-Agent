# DISTILL-CANARY-36b40d50 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
weights = {}
for row in csv.reader(io.StringIO(files["standards/hex_weights.csv"])):
    weights[int(row[0])] = int(row[1])
record = {}
for line in files["panels/controller_code_5531.txt"].splitlines():
    parts = line.split()
    if len(parts) == 2:
        record[parts[0]] = parts[1]
digits = "0123456789abcdef"
value = 0
for place, char in enumerate(reversed(record["controller_address"].lower())):
    value += digits.index(char) * weights[place]
print(json.dumps({"expected_number": value}))
