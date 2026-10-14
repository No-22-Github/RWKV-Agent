# DISTILL-CANARY-44d7e8c3 : distillation case
import json

case = json.load(open("case.json"))
log = case["files"]["sheets/extraction-2026-09-26.txt"]
lines = []
for row in log.splitlines():
    if not row.strip():
        continue
    hive, frames, grade = [p.strip() for p in row.split("/")]
    if grade == "A":
        lines.append("- %s - %s frames" % (hive, frames))
print(json.dumps({"files": {"labels/2026-09-26.txt": "\n".join(lines) + "\n"}}))
