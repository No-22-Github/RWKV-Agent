# DISTILL-CANARY-6b2c7ad8 : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["库存快照-2026-09-15.csv"]))
count = 0
for r in rows:
    if r["品类"].strip() != "生鲜":
        continue
    q = r["在库数量"].strip()
    try:
        float(q)
    except ValueError:
        continue
    count += 1
print(json.dumps({"expected_number": count}))
