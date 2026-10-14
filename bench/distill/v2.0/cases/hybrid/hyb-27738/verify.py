# DISTILL-CANARY-90f4c613 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = list(csv.DictReader(io.StringIO(case["files"]["finance/march_cashflow.csv"])))
income = sum(float(r["金额"]) for r in rows if r["类别"] == "收入")
refunds = [float(r["金额"]) for r in rows if r["类别"] == "退款"]
print(json.dumps({
    "expected_number": round(income - sum(refunds), 2),
    "turn_2_expected_number": max(refunds),
}))
