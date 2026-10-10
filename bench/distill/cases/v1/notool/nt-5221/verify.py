# DISTILL-CANARY-9eca11fe : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
row = next(csv.DictReader(io.StringIO(case["files"]["rooms/crop_room.csv"])))
per_hour = float(row["volume_m3"]) * float(row["air_changes_per_h"])
answer = per_hour / 60.0
print(json.dumps({"expected_number": answer}))
