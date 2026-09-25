# DISTILL-CANARY-72f8a1de : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]["practice/inbox-directory.txt"].splitlines():
    procedure, mailbox = [part.strip() for part in line.split("|")]
    rows[procedure] = mailbox
print(json.dumps({"expected_string": rows["insurance claim forms"]}))
