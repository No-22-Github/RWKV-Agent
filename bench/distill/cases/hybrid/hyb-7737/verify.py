# DISTILL-CANARY-6d2c85ae : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["finance/purchases_q2.csv"]))
total = sum(float(r["amount_usd"]) for r in rows
            if r["item"].startswith("Toner cartridge"))
print(json.dumps({"expected_number": round(total, 2)}))
