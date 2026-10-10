# DISTILL-CANARY-f7cb30cc : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
speeds = {
    row["route"]: float(row["service_speed_kn"])
    for row in csv.DictReader(io.StringIO(files["fleet/service_speeds.csv"]))
}
table = {
    row["conversion"]: float(row["factor"])
    for row in csv.DictReader(io.StringIO(files["standards/speed_conversions.csv"]))
}
print(json.dumps({
    "expected_number": speeds["Kerrera Narrows"] * table["knot to kilometre per hour"]
}))
