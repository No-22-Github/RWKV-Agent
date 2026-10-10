# DISTILL-CANARY-f960e2c8 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["royalties/royalties.csv"]))
total = 0.0
for r in rows:
    if r["author"] == "Nadia Kowalczyk" and r["quarter"] == "Q2":
        total += float(r["amount_gbp"])
print(json.dumps({"expected_number": round(total, 2)}))
