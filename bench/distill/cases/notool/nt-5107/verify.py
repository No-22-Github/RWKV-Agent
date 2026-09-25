# DISTILL-CANARY-d80cc75b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["supplier/quotes-2026-09.csv"]))
fee = next(r["fee_eur"] for r in rows if r["part"] == "SEAL-40")
print(json.dumps({"expected_number": float(fee)}))
