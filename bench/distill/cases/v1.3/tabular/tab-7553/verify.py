# DISTILL-CANARY-2493698b : distillation case
import csv
import io
import json
from decimal import Decimal
from collections import defaultdict

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/collection_2026-09.csv"]))
tot = defaultdict(Decimal)
for r in rows:
    if r["流水月份"] == "2026-09" and r["奶源村"] != "合计":
        tot[r["奶源村"]] += Decimal(r["收购公斤"])
print(json.dumps({"expected_number": float(max(tot.values()))}))
