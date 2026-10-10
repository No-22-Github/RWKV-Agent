# DISTILL-CANARY-78ce73f4 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
import math
row = next(csv.DictReader(io.StringIO(case["files"]["roofs/pitch_cards.csv"])))
rise = float(row["rise"])
run = float(row["run"])
answer = float(row["plan_area_m2"]) * math.sqrt(rise * rise + run * run) / run
print(json.dumps({"expected_number": answer}))
