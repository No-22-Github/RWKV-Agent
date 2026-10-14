# DISTILL-CANARY-c5dc1591 : distillation case
import json

case = json.load(open("case.json"))
log = case["files"]["log/resets.txt"]
lines = []
for row in log.splitlines():
    if not row.strip():
        continue
    wall, grade, color = [p.strip() for p in row.split("/")[:3]]
    lines.append("- %s %s %s" % (wall, grade, color))
print(json.dumps({"files": {"cards/2026-09-28.txt": "\n".join(lines) + "\n"}}))
