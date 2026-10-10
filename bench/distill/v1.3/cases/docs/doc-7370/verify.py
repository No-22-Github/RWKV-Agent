# DISTILL-CANARY-8b7d8a68 : distillation case
import json

case = json.load(open("case.json"))
sheet = case["files"]["daylogs/tally-2026-09-26.txt"]
lines = []
for row in sheet.splitlines():
    if not row.strip():
        continue
    item, count = [p.strip() for p in row.split("/")[:2]]
    lines.append("- %s: %s" % (item, count))
print(json.dumps({"files": {"tallies/2026-09-26.txt": "\n".join(lines) + "\n"}}))
