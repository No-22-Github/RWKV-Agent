import csv
import io
import json

def money(cell):
    return float(cell.replace("$", "").replace(",", ""))

case = json.load(open("case.json"))
gross = sum(money(r["amount"]) for r in csv.DictReader(io.StringIO(case["files"]["orders_april.csv"])))
refunded = sum(money(r["amount"]) for r in csv.DictReader(io.StringIO(case["files"]["refunds_april.csv"])))
print(json.dumps({"expected_number": round(gross - refunded, 2)}))
