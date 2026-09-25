# DISTILL-CANARY-9318077c : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/manifest-push.log"].splitlines()
terminal = re.compile(r"^\S+ \S+ +batch (B-\d+) undelivered reason=\S+$")
undelivered = {m.group(1) for m in (terminal.match(line) for line in lines) if m}
print(json.dumps({"expected_number": len(undelivered)}))
