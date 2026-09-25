# DISTILL-CANARY-85126f0b : distillation case
import json

case = json.load(open("case.json"))
revisions = {}
for line in case["files"]["standards/revision-register.txt"].splitlines():
    standard, revision = [part.strip() for part in line.split("=")]
    revisions[standard] = revision
print(json.dumps({"expected_string": revisions["access control standard"]}))
