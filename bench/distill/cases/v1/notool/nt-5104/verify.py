# DISTILL-CANARY-fea831b5 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["counts/turnstile-2026-09.csv"]))
entries = next(int(r["entries"]) for r in rows if r["date"] == "2026-09-12" and r["gate"] == "North")
print(json.dumps({"expected_number": entries}))
