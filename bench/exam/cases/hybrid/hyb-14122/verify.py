# EXAM-CANARY-dcc78a76 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
import csv, io
rows = list(csv.DictReader(io.StringIO(case["files"]["data/refunds.csv"])))
big = max(rows, key=lambda r: float(r["amount"]))
text = case["files"]["notes/summary.md"] + "Largest refund: %s %s\n" % (big["refund_id"], big["amount"])
print(json.dumps({"expected_contains_any": [big["customer"].split()[0]], "files": {"notes/summary.md": text}}))
