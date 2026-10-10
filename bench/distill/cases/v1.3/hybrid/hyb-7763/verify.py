# DISTILL-CANARY-64d478d0 : distillation case
import json

case = json.load(open("case.json"))
lines = [l for l in case["files"]["inspections/inspection-2026-09-15.txt"].split("\n") if l]
print(json.dumps({"files": {"logs/dock-issues.md": "\n".join(lines) + "\n"}}))
