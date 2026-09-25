# DISTILL-CANARY-23e29ef1 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
tons = sum(
    float(row["quantity"])
    for row in csv.DictReader(io.StringIO(files["orders/po_4471.csv"]))
)
table = {
    row["conversion"]: float(row["factor"])
    for row in csv.DictReader(io.StringIO(files["standards/mill_conversions.csv"]))
}
print(json.dumps({
    "expected_number": tons * table["short ton to pound"] / table["wheat bushel to pound"]
}))
