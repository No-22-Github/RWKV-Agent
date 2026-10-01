# DISTILL-CANARY-5e8406ff : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["gear/cameras.csv"]))
row = next(r for r in rows if r["camera"] == "白鲸一号")
w, h = row["resolution_px"].split("x")
print(json.dumps({"expected_number": int(w) * int(h) / 10000}))
