# DISTILL-CANARY-3058e9b4 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
row = next(csv.DictReader(io.StringIO(case["files"]["groups/trunk_loading.csv"])))
answer = float(row["speech_minutes_per_hour"]) / 60.0
print(json.dumps({"expected_number": answer}))
