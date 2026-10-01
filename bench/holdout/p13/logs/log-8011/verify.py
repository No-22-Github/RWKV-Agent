# DISTILL-CANARY-86cf7530 : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json

case = json.load(open("case.json"))
roster = {}
for r in csv.DictReader(io.StringIO(case["files"]["服务清单.csv"])):
    roster[r["服务名称"].strip()] = r["服务代码"].strip()
code = roster["支付回调服务"]
count = sum(
    1
    for line in case["files"]["gateway-20260912.log"].splitlines()
    if "[ERROR]" in line and code in line
)
print(json.dumps({"expected_number": count}))
