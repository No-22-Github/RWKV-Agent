# DISTILL-CANARY-47a0d8be : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/members_october.csv"])))
mrr = sum(float(r["monthly_fee"]) for r in rows if r["plan"] == "Standard")
joined = sum(1 for r in rows
             if r["plan"] == "Standard" and r["joined"].startswith("2026-09"))
print(json.dumps({
    "expected_number": round(mrr, 2),
    "turn_2_expected_number": joined,
}))
