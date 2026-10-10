# DISTILL-CANARY-e58ff980 : distillation case
import csv
import io
import json
from collections import defaultdict

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/packing_2026-09.csv"]))
tot = defaultdict(int)
for r in rows:
    if r["批次月份"] == "2026-09":
        tot[r["单品"]] += int(r["出厂箱数"])
print(json.dumps({"expected_number": max(tot.values())}))
