# DISTILL-CANARY-bd767df5 : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["发布记录-2026-09.csv"]))
count = sum(
    1
    for r in rows
    if r["环境"].strip() == "生产" and r["结果"].strip() == "失败"
)
print(json.dumps({"expected_number": count}))
