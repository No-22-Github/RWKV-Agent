# DISTILL-CANARY-f30b72c8 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["finance/butter_september.csv"]))
amounts = [float(r["金额"]) for r in rows]
print(json.dumps({
    "expected_number": round(sum(amounts), 2),
    "turn_2_expected_number": max(amounts),
}))
