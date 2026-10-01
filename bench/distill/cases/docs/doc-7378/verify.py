# DISTILL-CANARY-2a1bcd38 : distillation case
import json

case = json.load(open("case.json"))
rows = case["files"]["orders/2026-09.txt"]
lines = []
for row in rows.splitlines()[1:]:
    if not row.strip():
        continue
    f = row.split()
    if f[3] == "未提":
        lines.append("- %s %s %s %s" % (f[0], f[1], f[2], f[4]))
print(json.dumps({"files": {"pickup/提货单-2026-09-28.txt": "\n".join(lines) + "\n"}}))
