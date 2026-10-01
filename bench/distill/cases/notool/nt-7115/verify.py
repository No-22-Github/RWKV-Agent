# DISTILL-CANARY-33500b64 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["lab/setpoints.csv"]))
c = next(float(r["设定温度摄氏度"]) for r in rows if r["区域"] == "恒温间")
value = c * 9 / 5 + 32
print(json.dumps({"expected_number": value}))
