# DISTILL-CANARY-c74a09fd : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["logs/bread_production.csv"]))
total = sum(int(r["条数"]) for r in rows
            if r["品种"] == "全麦吐司" and "2026-09-07" <= r["date"] <= "2026-09-13")
print(json.dumps({"expected_number": total}))
