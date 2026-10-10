# DISTILL-CANARY-4d1e70a3 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]["operations/queue-ownership.txt"].splitlines():
    queue, desk = [part.strip() for part in line.split("=")]
    rows[queue] = desk
print(json.dumps({"expected_string": rows["burst pipe reports"]}))
