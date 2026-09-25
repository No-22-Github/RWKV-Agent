# DISTILL-CANARY-3a5f8d10 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["cable/pump_feeders.csv"])))
feeder = [row for row in rows if row["feeder"] == "PC-3"][0]
answer = float(feeder["three_core_mv_a_m"]) * float(feeder["current_a"]) * float(feeder["run_m"]) / 1000.0
print(json.dumps({"expected_number": answer}))
