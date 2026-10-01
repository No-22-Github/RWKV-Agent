# DISTILL-CANARY-33deb2f4 : distillation case
import json

case = json.load(open("case.json"))
rows = case["files"]["archives/repair-2026-09.txt"]
lines = []
for row in rows.splitlines():
    if not row.strip():
        continue
    f = row.split()
    if f[2] == "待修":
        lines.append("- %s %s" % (f[0], f[1]))
print(json.dumps({"files": {"pending/2026-09-26.txt": "\n".join(lines) + "\n"}}))
