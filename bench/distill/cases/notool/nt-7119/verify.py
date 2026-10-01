# DISTILL-CANARY-085c5034 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["parking/tariff.csv"]))
first = next(float(r["费用元"]) for r in rows if r["计费段"] == "首小时")
half = next(float(r["费用元"]) for r in rows if r["计费段"] == "此后每半小时")
value = first + (3.5 - 1) * 2 * half
print(json.dumps({"expected_number": value}))
