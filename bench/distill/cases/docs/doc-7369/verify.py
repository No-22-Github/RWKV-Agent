# DISTILL-CANARY-cba0f71e : distillation case
import json

case = json.load(open("case.json"))
sheet = case["files"]["daylogs/2026-09-28.txt"]
lines = []
for row in sheet.splitlines():
    if not row.strip():
        continue
    item, qty, status = [p.strip() for p in row.split("/")]
    if status == "order":
        lines.append("- %s x%s" % (item, qty))
print(json.dumps({"files": {"purchasing/2026-09-28.txt": "\n".join(lines) + "\n"}}))
