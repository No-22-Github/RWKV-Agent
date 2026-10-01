# DISTILL-CANARY-8175a362 : distillation case
import json

case = json.load(open("case.json"))
rows = case["files"]["records/loss-2026-09-27.txt"]
lines = []
for row in rows.splitlines():
    if not row.strip():
        continue
    f = row.split()
    if f[4] == "报废":
        lines.append("- %s %s %s" % (f[0], f[1], f[2]))
print(json.dumps({"files": {"restock/2026-09-27.txt": "\n".join(lines) + "\n"}}))
