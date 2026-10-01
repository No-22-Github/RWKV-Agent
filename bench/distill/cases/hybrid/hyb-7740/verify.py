# DISTILL-CANARY-15d7e90c : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["data/october_sessions.csv"]))
total = sum(int(r["节数"]) for r in rows if r["date"].startswith("2026-10"))
print(json.dumps({"expected_number": total}))
