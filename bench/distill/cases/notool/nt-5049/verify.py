# DISTILL-CANARY-6864927b : distillation case
import json

case = json.load(open("case.json"))
formats = {}
for line in case["files"]["conventions/handoff-format.txt"].splitlines():
    handoff, extension = [part.strip() for part in line.split("=")]
    formats[handoff] = extension
print(json.dumps({"expected_string": formats["article handoffs"]}))
