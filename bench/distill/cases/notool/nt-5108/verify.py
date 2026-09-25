# DISTILL-CANARY-c6262477 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["figures/august-2026.csv"]))
amount = next(r["amount_gbp"] for r in rows if r["line"] == "F-01")
print(json.dumps({"expected_number": float(amount)}))
