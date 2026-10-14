# DISTILL-CANARY-c9d27e38 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
mapping = {"D": "白班", "N": "夜班"}
rows = csv.DictReader(io.StringIO(case["files"]["roster/shifts_2026w41.csv"]))
code = next(r["code"] for r in rows if r["name"] == "赵磊" and r["day"] == "2026-10-08")
print(json.dumps({"expected_string": mapping[code]}))
