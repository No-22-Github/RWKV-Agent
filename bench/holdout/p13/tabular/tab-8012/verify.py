# DISTILL-CANARY-d2c7fcfa : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["returns/退货明细-2026-09.csv"]))
count = 0
for r in rows:
    if r["退货单号"].strip() == "合计" or r["申请日期"].strip() == "":
        continue
    if r["状态"].strip() == "已完成":
        count += 1
print(json.dumps({"expected_number": count}))
