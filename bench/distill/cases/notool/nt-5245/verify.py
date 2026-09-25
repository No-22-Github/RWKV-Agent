# DISTILL-CANARY-d56ff13a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rates = {}
for row in csv.reader(io.StringIO(files["standards/depth_units.csv"])):
    rates[row[0]] = float(row[1])
record = {}
for line in files["surveys/channel_survey_2264.txt"].splitlines():
    parts = line.split()
    if len(parts) == 2:
        record[parts[0]] = parts[1]
print(json.dumps({
    "expected_number": float(record["design_depth_fathoms"]) * rates["metre_per_fathom"]
}))
