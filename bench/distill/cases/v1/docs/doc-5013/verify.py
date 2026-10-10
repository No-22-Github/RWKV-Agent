# DISTILL-CANARY-08f5a2c9 : distillation case
import json

case = json.load(open("case.json"))
lines = [line.strip() for line in case["files"]["checklist.txt"].splitlines() if line.strip()]

# The checklist is read by stage: everything under the registration heading and
# above the next heading is what a new client hands in at the desk.
count = 0
in_registration = False
for line in lines:
    if line == "Hand in at registration":
        in_registration = True
    elif line == "Bring to the first visit":
        in_registration = False
    elif in_registration:
        count += 1

print(json.dumps({"expected_number": count}))
