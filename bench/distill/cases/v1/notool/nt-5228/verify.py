# DISTILL-CANARY-8fe4c82e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
row = next(csv.DictReader(io.StringIO(case["files"]["groups/call_profile.csv"])))
minutes = float(row["calls_in_hour"]) * float(row["mean_holding_min"])
answer = minutes / 60.0
print(json.dumps({"expected_number": answer}))
