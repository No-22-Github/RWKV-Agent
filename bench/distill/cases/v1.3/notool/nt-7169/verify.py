# DISTILL-CANARY-6e06f9ff : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["gear/speaker_list.csv"])))
mains = [float(r["impedance_ohm"]) for r in rows if r["spot"] == "试音间"]
if len(mains) != 2:
    sys.exit("expected exactly two mains wired on the demo-room output")
print(json.dumps({"expected_number": mains[0] * mains[1] / (mains[0] + mains[1])}))
