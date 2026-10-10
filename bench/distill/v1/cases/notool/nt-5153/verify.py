# DISTILL-CANARY-1f7b90d4 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]["records/archive-map.txt"].splitlines():
    record, place = [part.strip() for part in line.split("=")]
    rows[record] = place
print(json.dumps({"expected_string": rows["calving records"]}))
