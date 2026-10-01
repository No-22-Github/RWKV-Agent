# DISTILL-CANARY-01c14745 : distillation case
import json

case = json.load(open("case.json"))
log = case["files"]["daylogs/2026-09-27.txt"]
lines = []
for row in log.splitlines():
    if not row.strip():
        continue
    name, seat = [p.strip() for p in row.split("/")[:2]]
    lines.append("- %s / %s" % (name, seat))
print(json.dumps({"files": {"notices/2026-09-27.txt": "\n".join(lines) + "\n"}}))
