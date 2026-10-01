# DISTILL-CANARY-ce96a40d : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["admin/meeting_rooms.csv"]))
area = next(float(r["area_sqm"]) for r in rows if r["room"] == "大会议室")
print(json.dumps({"expected_number": area / 2}))
