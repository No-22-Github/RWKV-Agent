# DISTILL-CANARY-5ea17dc9 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["reference/shutter_pair.csv"])))
times = [(r["shutter"], float(r["exposure_seconds"])) for r in rows]
t = dict(times)
# A shorter exposure time is a faster shutter.
expected = "快" if t["1/250"] < t["1/125"] else "慢"
print(json.dumps({"expected_string": expected}))
