# DISTILL-CANARY-dd3abe58 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["packaging/keg_runs_2026-09.csv"])))
kegs = sum(float(row["kegs"]) for row in rows)
gallon_per_keg = sum(float(row["keg_size_gal"]) for row in rows) / len(rows)
table = {
    row["conversion"]: float(row["factor"])
    for row in csv.DictReader(io.StringIO(files["standards/brewery_conversions.csv"]))
}
print(json.dumps({
    "expected_number": kegs * gallon_per_keg / table["US beer barrel to US gallon"]
}))
