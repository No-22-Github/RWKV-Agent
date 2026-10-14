# DISTILL-CANARY-8947a06b : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["inventory/stock-positions.tsv"]), delimiter="\t"))

target = [r for r in rows if r["sku"] == "RLC-4417"]
if len(target) != 1:
    raise SystemExit(f"fixture guard failed: RLC-4417 appears {len(target)} times")
for near, price in (("RLC-4147", "2.95"), ("RLC-4417A", "4.10")):
    hits = [r for r in rows if r["sku"] == near]
    if len(hits) != 1 or hits[0]["unit_cost_gbp"] != price:
        raise SystemExit(f"fixture guard failed: near-name {near} is gone or repriced")
row = target[0]
value = Decimal(row["qty_on_hand"]) * Decimal(row["unit_cost_gbp"])
print(json.dumps({"expected_number": float(value)}))
