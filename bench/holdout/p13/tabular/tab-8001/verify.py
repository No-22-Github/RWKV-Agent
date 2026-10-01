# DISTILL-CANARY-054f4b50 : p13-holdout eval case (eval-only, never training data)
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.reader(io.StringIO(case["files"]["exports/orders-2026-09.csv"])))
header = [cell.strip().lower() for cell in rows[0]]
if not {"order_ref", "amount"} <= set(header):
    raise SystemExit("orders export layout changed; the column check is void")
if any("refund" in cell for cell in header):
    raise SystemExit("refund column present; the absence expectation is void")
print(json.dumps({"expected_contains_any": ["refund", "refunds", "refunded"]}))
