# DISTILL-CANARY-97c7478e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["invoices/q3-eu.csv"])))
total = round(sum(float(r["amount_eur"]) for r in rows if r["client"] == "Brightwater Marine"), 2)
print(json.dumps({"expected_number": total}))
