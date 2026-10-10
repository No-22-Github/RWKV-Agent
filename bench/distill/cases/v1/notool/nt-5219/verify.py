# DISTILL-CANARY-78ff064b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
row = next(csv.DictReader(io.StringIO(case["files"]["timber/plank_schedule.csv"])))
answer = float(row["thickness_in"]) * float(row["width_in"]) * float(row["length_ft"]) / 12.0
print(json.dumps({"expected_number": answer}))
