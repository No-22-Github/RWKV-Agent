# DISTILL-CANARY-9fcdc888 : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["2026-活动预算表.csv"]))
total = sum(
    float(r["预算(元)"])
    for r in rows
    if r["所属会议"].strip() == "0914 例会" and r["状态"].strip() == "已确认"
)
print(json.dumps({"expected_number": round(total, 2)}))
