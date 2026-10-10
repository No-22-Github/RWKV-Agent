# DISTILL-CANARY-d2319730 : distillation case
import csv
import io
import json
from collections import defaultdict

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/wholesale_2026-08.csv"]))
tot = defaultdict(int)
for r in rows:
    if r["出货月份"] == "2026-08":
        tot[r["批发市场"]] += int(r["板数"])
print(json.dumps({"expected_number": max(tot.values())}))
