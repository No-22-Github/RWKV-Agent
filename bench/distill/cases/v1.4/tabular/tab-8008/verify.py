# DISTILL-CANARY-9daa1205 : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json"))
assert "日-月-年" in case["files"]["README.md"]
n = 0
for r in csv.DictReader(io.StringIO(case["files"]["物流/发货记录.csv"])):
    s = r["发货日期"]
    m = re.match(r"2026/03/(\d\d)$", s) or re.match(r"(\d\d)-03-2026$", s) or re.match(r"Mar (\d+), 2026$", s) or re.match(r"2026-03-(\d\d)T", s)
    assert m, s
    n += int(m.group(1)) <= 10
print(json.dumps({"expected_number": n}))
