# DISTILL-CANARY-ec8871fb : distillation case
import json

case = json.load(open("case.json"))
log = case["files"]["daylogs/2026-09-24.txt"]
lines = []
for row in log.splitlines():
    if not row.strip():
        continue
    name, seat, status = [p.strip() for p in row.split("/")[:3]]
    if status == "cleared":
        lines.append("- %s (%s)" % (name, seat))
print(json.dumps({"files": {"rosters/2026-09-24.txt": "\n".join(lines) + "\n"}}))
