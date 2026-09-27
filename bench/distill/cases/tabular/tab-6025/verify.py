# DISTILL-CANARY-a44e138a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["region/invoices_2026-07.csv"])))
per = {}
for r in rows:
    val = float(r["amount"].replace("$", "").replace(",", ""))
    per[r["region"]] = per.get(r["region"], 0.0) + val
print(json.dumps({"expected_number": round(max(per.values()), 2)}))
