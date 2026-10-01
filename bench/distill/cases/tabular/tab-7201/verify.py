# DISTILL-CANARY-9de28730 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/sales-lines-2026-05.csv"])))

orders = {}
rowcount = {}
line_seen = {}
dups = 0
for r in rows:
    sku = r["sku"]
    orders.setdefault(sku, set()).add(r["order_id"])
    rowcount[sku] = rowcount.get(sku, 0) + 1
    sig = r["order_id"] + r["order_date"] + r["sku"] + r["qty"]
    if r["line_id"] in line_seen:
        if line_seen[r["line_id"]] != sig:
            raise SystemExit("fixture guard failed: repeated line_id differs")
        dups += 1
    line_seen[r["line_id"]] = sig

if dups < 1:
    raise SystemExit("fixture guard failed: the retried export re-sent lines are gone")
ranked = sorted(orders.items(), key=lambda kv: (-len(kv[1]), kv[0]))
if len(ranked[1][1]) == len(ranked[0][1]):
    raise SystemExit("fixture guard failed: tie at the top of the order ranking")
rows_leader = max(rowcount.items(), key=lambda kv: (kv[1], kv[0]))
if rows_leader[0] == ranked[0][0]:
    raise SystemExit("fixture guard failed: row leader equals order leader")
print(json.dumps({"expected": ranked[0][0]}))
