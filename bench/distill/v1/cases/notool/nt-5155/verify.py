# DISTILL-CANARY-a57d2b61 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]["office/archive-map.txt"].splitlines():
    record, place = [part.strip() for part in line.split("=")]
    rows[record] = place
print(json.dumps({"expected_string": rows["ringing permits"]}))
