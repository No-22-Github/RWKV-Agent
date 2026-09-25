# DISTILL-CANARY-cc351ff2 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["bars/bar_ledger_2026-09.csv"])))
pints = sum(float(row["drinks"]) for row in rows)
fl_oz_per_pint = sum(float(row["pour_fl_oz"]) for row in rows) / len(rows)
table = {
    row["conversion"]: float(row["factor"])
    for row in csv.DictReader(io.StringIO(files["standards/volume_conversions.csv"]))
}
print(json.dumps({
    "expected_number": pints * fl_oz_per_pint / table["US gallon to US fluid ounce"]
}))
