# DISTILL-CANARY-86a3343f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["plans/floor_areas.csv"]))
area = next(float(r["面积平方米"]) for r in rows if r["区域"] == "开放办公区")
value = area / 3
print(json.dumps({"expected_number": value}))
