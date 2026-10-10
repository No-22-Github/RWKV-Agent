# DISTILL-CANARY-973dbf25 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/stalls_2026-09.csv"]))
vens = set()
for r in rows:
    if r["trade_date"] in ("2026-09-05", "05/09/2026"):
        vens.add(r["vendor_code"])
print(json.dumps({"expected_number": len(vens)}))
