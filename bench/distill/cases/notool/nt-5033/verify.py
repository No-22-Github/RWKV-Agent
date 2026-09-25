# DISTILL-CANARY-932a862a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["cabinets/so_3312.csv"])))
units = float([row for row in rows if row["item"].startswith("Fairline")][0]["height_u"])
table = {
    row["conversion"]: float(row["factor"])
    for row in csv.DictReader(io.StringIO(files["standards/rack_conversions.csv"]))
}
print(json.dumps({
    "expected_number": units * table["U to millimetre"] / 10.0
}))
