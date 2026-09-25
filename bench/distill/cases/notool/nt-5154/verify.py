# DISTILL-CANARY-63c0e8fa : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]["admin/record-storage.txt"].splitlines():
    record, place = [part.strip() for part in line.split("=")]
    rows[record] = place
print(json.dumps({"expected_string": rows["pupil safeguarding files"]}))
