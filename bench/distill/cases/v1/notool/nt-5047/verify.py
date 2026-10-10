# DISTILL-CANARY-3a62f93d : distillation case
import json

case = json.load(open("case.json"))
patterns = {}
for line in case["files"]["conventions/branch-naming.txt"].splitlines():
    name, prefix = [part.strip() for part in line.split(":")]
    patterns[name] = prefix
print(json.dumps({"expected_string": patterns["feature branches"]}))
