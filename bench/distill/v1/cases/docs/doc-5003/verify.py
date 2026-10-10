# DISTILL-CANARY-a2f6d08b : distillation case
import json

case = json.load(open("case.json"))
lines = [line.strip() for line in case["files"]["checklist.txt"].splitlines() if line.strip()]

# The checklist is read by stage: everything under the enrolment heading and
# above the next heading is what a joiner hands in at enrolment.
count = 0
in_enrolment = False
for line in lines:
    if line == "Items to hand in at enrolment":
        in_enrolment = True
    elif line == "Items to hand in before the first session":
        in_enrolment = False
    elif in_enrolment:
        count += 1

print(json.dumps({"expected_number": count}))
