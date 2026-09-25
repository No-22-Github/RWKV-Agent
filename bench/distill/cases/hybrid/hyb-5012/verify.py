# DISTILL-CANARY-19a4d75f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["orders/dundalk-2026-09.csv"]))
total = sum(int(row["crates"]) * float(row["price_eur"]) for row in rows)
print(json.dumps({"expected_number": round(total, 2)}))
