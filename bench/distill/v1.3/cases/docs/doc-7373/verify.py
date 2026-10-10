# DISTILL-CANARY-be745064 : distillation case
import json

case = json.load(open("case.json"))
log = case["files"]["log/resets.txt"]
lines = []
seen = set()
for row in log.splitlines():
    if not row.strip():
        continue
    wall, grade, color, status = [p.strip() for p in row.split("/")]
    if status != "set" or (wall, grade, color) in seen:
        continue
    seen.add((wall, grade, color))
    lines.append("- %s %s %s" % (wall, grade, color))
print(json.dumps({"files": {"cards/2026-09-25.txt": "\n".join(lines) + "\n"}}))
