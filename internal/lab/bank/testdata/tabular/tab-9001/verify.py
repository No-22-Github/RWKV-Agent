import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["orders.csv"])))
refund = sum(float(r["amount"]) for r in csv.DictReader(io.StringIO(files["refunds.csv"])))
total = sum(float(r["amount"]) for r in rows) - refund
print(json.dumps({"expected_number": total}))
