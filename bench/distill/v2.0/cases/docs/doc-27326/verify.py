# DISTILL-CANARY-74528ac4 : distillation case
import csv, io, json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["docs/积分规则.csv"]))
values = sorted({r["积分有效期(月)"] for r in rows if r["卡种"] == "银卡"})
value = values[0]
print(json.dumps({"expected_contains_any": [value + " 个月", value + "个月"]}))
