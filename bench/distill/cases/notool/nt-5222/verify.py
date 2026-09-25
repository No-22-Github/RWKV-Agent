# DISTILL-CANARY-e083f6dd : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
row = next(csv.DictReader(io.StringIO(case["files"]["rooms/air_handling.csv"])))
answer = float(row["supply_m3_per_h"]) / float(row["volume_m3"])
print(json.dumps({"expected_number": answer}))
