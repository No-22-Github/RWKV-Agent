# DISTILL-CANARY-3a17f4c8 : distillation case
import json

case = json.load(open("case.json"))
settings = case["files"]["config/cell.yaml"]

# README.md: every value the cell runs with comes from this file, and
# spindle_rpm is the speed it runs at.
value = None
for line in settings.splitlines():
    key, _, raw = line.partition(":")
    if key.strip() == "spindle_rpm":
        value = int(raw.strip())

print(json.dumps({"expected_number": value}))
