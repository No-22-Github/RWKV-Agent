# DISTILL-CANARY-4dd919fb : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json
import re

case = json.load(open("case.json"))
memo = case["files"]["提成办法.md"]
base_rate = int(re.search(r"按订单金额的 (\d+)%", memo).group(1)) / 100.0
threshold = float(re.search(r"满 (\d+) 元", memo).group(1))
over_rate = int(re.search(r"超出 \d+ 元的部分按 (\d+)%", memo).group(1)) / 100.0

rows = csv.DictReader(io.StringIO(case["files"]["sales/销售明细-2026-09.csv"]))
total = 0.0
for r in rows:
    if r["类型"].strip() != "销售":
        continue
    amount = float(r["金额(元)"])
    if amount > threshold:
        total += threshold * base_rate + (amount - threshold) * over_rate
    else:
        total += amount * base_rate
print(json.dumps({"expected_number": round(total, 2)}))
