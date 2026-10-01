# DISTILL-CANARY-3e8b52d7 : p13 holdout (eval-only)
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
orders = list(csv.DictReader(io.StringIO(case["files"]["finance/orders-2026-09.csv"])))
receipts = list(csv.DictReader(io.StringIO(case["files"]["finance/receipts-2026-09.csv"])))
received = {
    r["order_id"] for r in receipts
    if not (r["amount"].strip() == "0" and r["note"].strip() == "占位")
}
missing = sorted(o["order_id"] for o in orders if o["order_id"] not in received)
content = "\n".join(missing) + "\n"
print(json.dumps({"files": {
    "reports/unreceipted-2026-09.txt": content,
    "finance/README.md": case["files"]["finance/README.md"],
    "finance/orders-2026-09.csv": case["files"]["finance/orders-2026-09.csv"],
    "finance/receipts-2026-09.csv": case["files"]["finance/receipts-2026-09.csv"],
}}))
