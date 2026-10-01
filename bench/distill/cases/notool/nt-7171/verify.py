# DISTILL-CANARY-d00a8eba : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["garden/tank_log.csv"]))
row = next(r for r in rows if r["vessel"] == "喷壶A")
print(json.dumps({"expected_number": float(row["volume_l"]) * 1000 / 500}))
