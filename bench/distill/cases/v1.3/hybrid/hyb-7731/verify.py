# DISTILL-CANARY-0d84a6b1 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = list(csv.DictReader(io.StringIO(case["files"]["logs/receiving_september.csv"])))
stems = sum(int(r["stems"]) for r in rows
            if r["item"] == "Roses" and r["date"] == "2026-09-14")
credit = sum(float(r["credit_usd"]) for r in rows)
print(json.dumps({
    "expected_number": stems,
    "turn_2_expected_number": round(credit, 2),
}))
