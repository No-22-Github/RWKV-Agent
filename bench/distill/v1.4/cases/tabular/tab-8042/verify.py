# DISTILL-CANARY-1b6cd75d : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
# Sabotage target: 产值/9月维修产值.csv sorts first in the corruption order; pin its first line.
assert files['产值/9月维修产值.csv'].splitlines()[0] == '工单号,日期,门店,产值'

import csv
import io

rows = list(csv.DictReader(io.StringIO(files["产值/9月维修产值.csv"])))
total = round(sum(float(r["产值"]) for r in rows if r["门店"] == "开发区店"), 2)
assert total == 46918.88
wan2 = "%.2f" % (total / 10000)
assert wan2 == '4.69'
words = ['46918.88', '46,918.88', '4.69']
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
