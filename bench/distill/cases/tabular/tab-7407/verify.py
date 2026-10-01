# DISTILL-CANARY-f30b47ce : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/workorders.csv"]))
orders = {
    r["工单号"]
    for r in rows
    if r["片区"] == "高新" and r["工单月份"] == "2026-09"
}
print(json.dumps({"expected_number": len(orders)}))
