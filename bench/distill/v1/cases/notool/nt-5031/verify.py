# DISTILL-CANARY-8521fa8c : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
tons = sum(
    float(row["quantity"])
    for row in csv.DictReader(io.StringIO(files["berths/discharge_2026-09.csv"]))
)
table = {
    row["conversion"]: float(row["factor"])
    for row in csv.DictReader(io.StringIO(files["standards/port_conversions.csv"]))
}
print(json.dumps({
    "expected_number": tons * table["long ton to pound"]
}))
