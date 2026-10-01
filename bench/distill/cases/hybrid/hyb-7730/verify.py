# DISTILL-CANARY-71c9f3e4 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["suppliers_2026.csv"]))
terms = next(int(r["terms_days"]) for r in rows if r["supplier"] == "青云花材")
print(json.dumps({"expected_number": terms}))
