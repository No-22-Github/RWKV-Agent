# DISTILL-CANARY-e25f9219 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["assets/lift_plates.csv"]))
load_t = next(float(r["额定载重吨"]) for r in rows if r["电梯"] == "3号货梯")
value = load_t * 1000
print(json.dumps({"expected_number": value}))
