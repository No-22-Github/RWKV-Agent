# DISTILL-CANARY-b7e40c92 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
card = next(csv.DictReader(io.StringIO(case["files"]["cable/drop_schedule.csv"])))
answer = float(card["two_core_mv_a_m"]) * float(card["current_a"]) * float(card["run_m"]) / 1000.0
print(json.dumps({"expected_number": answer}))
