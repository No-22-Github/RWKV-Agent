# DISTILL-CANARY-f35b6bfc : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json
import re
import sys

case = json.load(open("case.json"))
row = None
for r in csv.DictReader(io.StringIO(case["files"]["stores.csv"])):
    if r["门店"].strip() == "徐汇店":
        row = r
if row is None:
    sys.exit(1)
diff_rate = float(row["差异费率(千分比)"])
floor_m = re.search(r"低于 ([\d.]+) 时按 ([\d.]+)", case["files"]["cities.yaml"])
if not floor_m:
    sys.exit(1)
floor = float(floor_m.group(1))
effective = floor if diff_rate < floor else diff_rate
print(json.dumps({"expected_number": effective}))
