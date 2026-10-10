# DISTILL-CANARY-dd40cb0f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["subscriptions/subs_2026Q3.csv"])))
owed = sum(float(r["amount_due"]) - float(r["amount_paid"]) for r in rows)
print(json.dumps({"expected_number": round(owed, 2)}))
