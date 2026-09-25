# DISTILL-CANARY-208e584e : distillation case
import json

case = json.load(open("case.json"))
revisions = {}
for line in case["files"]["standards/workshop-standards.txt"].splitlines():
    standard, revision = [part.strip() for part in line.split("=")]
    revisions[standard] = revision
print(json.dumps({"expected_string": revisions["air quality standard"]}))
