import csv
import io
import json

case = json.load(open("case.json"))
billed = sum(float(r["amount"]) for r in csv.DictReader(io.StringIO(case["files"]["invoices.csv"])))
credits = sum(float(r["amount"]) for r in csv.DictReader(io.StringIO(case["files"]["credit-notes.csv"])))
print(json.dumps({"expected_number": round(billed - credits, 2)}))
