# DISTILL-CANARY-d09b47ea : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = list(csv.DictReader(io.StringIO(case["files"]["logs/develops.csv"])))
april_color = sum(int(r["卷数"]) for r in rows
                  if r["月份"] == "4" and r["类型"] == "彩色")
may_bw = sum(int(r["卷数"]) for r in rows
             if r["月份"] == "5" and r["类型"] == "黑白")
print(json.dumps({
    "expected_number": april_color,
    "turn_2_expected_number": may_bw,
}))
