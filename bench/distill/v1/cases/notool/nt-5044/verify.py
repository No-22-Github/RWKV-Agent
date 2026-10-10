# DISTILL-CANARY-5d504deb : distillation case
import json

case = json.load(open("case.json"))
prefixes = {}
for line in case["files"]["procedures/ticket-prefixes.txt"].splitlines():
    name, code = [part.strip() for part in line.split("->")]
    prefixes[name] = code
print(json.dumps({"expected_string": prefixes["access review request"]}))
