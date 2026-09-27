# DISTILL-CANARY-dbb23b85 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["statements/fm-4471_statement.csv"])))
balance = sum(float(r["amount"]) for r in rows)
print(json.dumps({"expected_number": round(balance, 2)}))
