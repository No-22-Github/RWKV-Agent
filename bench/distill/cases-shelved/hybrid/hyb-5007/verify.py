# DISTILL-CANARY-c84d17ab : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["invoices/september-jobs.csv"]))
total = sum(float(row["amount_gbp"]) for row in rows if row["site"] == "Lamont Wharf")
print(json.dumps({"expected_number": round(total, 2)}))
