# DISTILL-CANARY-6871a964 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/gongdan-2026-09.csv"])))
orders = set()
n = 0
for r in rows:
    if r["网点"] == "城北网点":
        orders.add(r["工单号"])
        n += 1
if n <= len(orders):
    raise SystemExit("fixture guard failed: the retried rows are gone")
print(json.dumps({"expected_number": len(orders)}))
