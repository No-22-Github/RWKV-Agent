# DISTILL-CANARY-126f5374 : distillation case
import csv
import io
import json
from decimal import Decimal

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/dingdan-2026-07.csv"])))

best = None
refund_top = None
for r in rows:
    amt = Decimal(r["金额"])
    if r["类型"] == "销售" and r["下单时间"][:10] >= "2026-07-20":
        if best is None or amt > best[0]:
            best = (amt, r["订单号"])
    if r["类型"] == "退货":
        if refund_top is None or amt > refund_top[0]:
            refund_top = (amt, r["订单号"])

if best is None:
    raise SystemExit("fixture guard failed: no sales order on or after 2026-07-20")
if refund_top is None or refund_top[0] <= best[0]:
    raise SystemExit("fixture guard failed: the positive-amount refund decoy is gone")
ties = [r for r in rows
        if r["类型"] == "销售" and r["下单时间"][:10] >= "2026-07-20"
        and Decimal(r["金额"]) == best[0]]
if len(ties) != 1:
    raise SystemExit("fixture guard failed: maximum sale amount is not unique")
print(json.dumps({"expected": best[1]}))
