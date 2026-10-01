# DISTILL-CANARY-84b4f275 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["logs/refunds-2026-09.csv"]))
lines = [",".join([r["refund_id"], r["date"], r["reason"], r["amount_gbp"]]) for r in rows]
print(json.dumps({"files": {"reports/refund-summary.md": "\n".join(lines) + "\n"}}))
