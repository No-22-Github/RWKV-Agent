# DISTILL-CANARY-1245423c : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["退款/2026-09.csv"])))
sums = {}
for r in rows:
    sums[r["渠道"]] = sums.get(r["渠道"], 0) + float(r["金额"])
print(json.dumps({"expected_number": round(sums["天猫"], 2)}))
