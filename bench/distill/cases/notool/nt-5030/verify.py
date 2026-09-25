# DISTILL-CANARY-1ce3b6e9 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
bushels = sum(
    float(row["bushels"])
    for row in csv.DictReader(io.StringIO(files["intake/loads_2026-09.csv"]))
)
table = {
    row["conversion"]: float(row["factor"])
    for row in csv.DictReader(io.StringIO(files["standards/grain_conversions.csv"]))
}
print(json.dumps({
    "expected_number": bushels * table["oat bushel to pound"]
}))
