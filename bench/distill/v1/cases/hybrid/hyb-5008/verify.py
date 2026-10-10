# DISTILL-CANARY-6fa20d39 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["orders/hallam-2026-09.csv"]))
total = sum(int(row["quantity"]) * float(row["unit_price_trade"]) for row in rows)
print(json.dumps({"expected_number": round(total, 2)}))
