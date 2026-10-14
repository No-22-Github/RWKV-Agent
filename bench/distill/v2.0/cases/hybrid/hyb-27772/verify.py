# DISTILL-CANARY-e5a1db92 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["records/收购台账.csv"]))
total = 0.0
for r in rows:
    if r["经手人"] == "陈晓芸" and r["班组"] == "收购二组":
        total += float(r["金额"])
print(json.dumps({"expected_number": round(total, 2)}))
