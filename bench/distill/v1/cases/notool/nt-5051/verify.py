# DISTILL-CANARY-3b998fec : distillation case
import json

case = json.load(open("case.json"))
revisions = {}
for line in case["files"]["standards/clinical-records.txt"].splitlines():
    standard, revision = [part.strip() for part in line.split("=")]
    revisions[standard] = revision
print(json.dumps({"expected_string": revisions["clinical records standard"]}))
