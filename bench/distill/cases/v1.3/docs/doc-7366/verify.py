# DISTILL-CANARY-fa623470 : distillation case
import json
import re

case = json.load(open("case.json"))
best = None
for path in ("current/availability.txt", "prior/availability.txt"):
    text = case["files"][path]
    head = text.splitlines()[0]
    m = re.search(r"effective (\d{4}-\d{2}-\d{2})", head)
    if not m:
        raise SystemExit("no effective date in " + path)
    if best is None or m.group(1) > best[0]:
        best = (m.group(1), text)
lines = []
for row in best[1].splitlines()[1:]:
    if not row.strip():
        continue
    name, packets, note = [p.strip() for p in row.split("/")]
    if "on hold" in note:
        continue
    lines.append("- %s (%s packets)" % (name, packets))
print(json.dumps({"files": {"handouts/2026-09-29.txt": "\n".join(lines) + "\n"}}))
