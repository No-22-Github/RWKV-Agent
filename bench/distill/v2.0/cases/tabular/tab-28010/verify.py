# DISTILL-CANARY-e87f80fd : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
f = case["files"]
roster = list(csv.DictReader(io.StringIO(f["人事/花名册.csv"])))
rd = {r["工号"] for r in roster if r["部门"] == "研发部"}
hours = list(csv.DictReader(io.StringIO(f["考勤/2026-09-工时.csv"])))
print(json.dumps({"expected_number": sum(float(h["小时"]) for h in hours if h["工号"] in rd and h["类型"] == "加班")}))
