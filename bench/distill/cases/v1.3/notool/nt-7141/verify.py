# DISTILL-CANARY-e3f82386 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["frames/frames.csv"]))
width_cm = next(float(r["width_cm"]) for r in rows if r["frame_no"] == "K-118")
print(json.dumps({"expected_number": round(width_cm / 2.54, 2)}))
