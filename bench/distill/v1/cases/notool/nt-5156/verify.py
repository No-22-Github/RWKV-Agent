# DISTILL-CANARY-0ce4937b : distillation case
import json

case = json.load(open("case.json"))
rows = {}
for line in case["files"]["procedures/inbox-directory.txt"].splitlines():
    procedure, mailbox = [part.strip() for part in line.split("|")]
    rows[procedure] = mailbox
print(json.dumps({"expected_string": rows["tenancy fraud referral"]}))
