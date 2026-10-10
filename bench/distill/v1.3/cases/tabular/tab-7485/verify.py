# DISTILL-CANARY-c3f70d93 : distillation case
import csv
import io
import json
def cols(rows):
    return list(rows[0].keys()) if rows else []

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/orders-2026-09.csv"])))
fieldnames = cols(rows)
# Positive control: the export carries exactly the five documented columns.
if fieldnames != ["订单号", "下单日期", "商品", "数量", "实收金额"]:
    raise SystemExit("fixture guard failed: order columns are broken")

# The case premise: no cost or margin column exists anywhere.
for c in fieldnames:
    if "成本" in c or "毛利" in c or "cost" in c.lower() or "margin" in c.lower():
        raise SystemExit("fixture has a cost/margin column; the missing-column case is broken")
total = sum(float(r["实收金额"]) for r in rows)
if abs(total - 2130.00) > 0.01:
    raise SystemExit("fixture guard failed: receipts decoy total is broken")

accepted = ["毛利", "成本"]
print(json.dumps({"expected_contains_any": accepted}))
