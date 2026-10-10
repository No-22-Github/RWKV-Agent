# DISTILL-CANARY-82bfb705 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["invoices/invoices-issued.csv"]))
total = 0.0
for r in rows:
    if r["client"] == "Kestrel Homes":
        total += float(r["amount_gbp"])
print(json.dumps({"expected_number": round(total, 2)}))
