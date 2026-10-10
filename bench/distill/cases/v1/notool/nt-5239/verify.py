# DISTILL-CANARY-99f24834 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
scale = {}
for row in csv.reader(io.StringIO(files["standards/temperature_scale.csv"])):
    scale[row[0]] = float(row[1])
record = {}
for line in files["chambers/chamber_setting_5108.txt"].splitlines():
    parts = line.split()
    if len(parts) == 2:
        record[parts[0]] = parts[1]
above_freezing = float(record["setpoint_fahrenheit"]) - scale["freezing_point_fahrenheit"]
print(json.dumps({
    "expected_number": above_freezing / scale["fahrenheit_step_per_celsius_step"]
}))
