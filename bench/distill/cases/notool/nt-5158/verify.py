# DISTILL-CANARY-b9e64035 : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]["office/inbox-directory.txt"].splitlines():
    procedure, mailbox = [part.strip() for part in line.split("|")]
    rows[procedure] = mailbox
print(json.dumps({"expected_string": rows["grid export meter readings"]}))
