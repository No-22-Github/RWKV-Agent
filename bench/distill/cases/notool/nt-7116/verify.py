# DISTILL-CANARY-3dba915f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["fleet/speed_log.csv"]))
kmh = next(float(r["巡航时速千米每小时"]) for r in rows if r["车辆"] == "巡逻-01")
value = kmh * 1000 / 60
print(json.dumps({"expected_number": value}))
