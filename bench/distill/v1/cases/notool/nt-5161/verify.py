# DISTILL-CANARY-5c2f9a08 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]["office/signoff-list.txt"].splitlines():
    booking, role = [part.strip() for part in line.split("=")]
    rows[booking] = role
print(json.dumps({"expected_string": rows["boat lift bookings"]}))
