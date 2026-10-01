# DISTILL-CANARY-be8073ed : distillation case
import json

case = json.load(open("case.json"))
book = case["files"]["logbook/claims-2026-09.txt"]
sheet = case["files"]["notices/inspector-2026-09-28.txt"]
rows = [l for l in sheet.splitlines() if l.strip()]
date = rows[0].split()[-1]
new = []
seen = set()
for row in rows[1:]:
    berth, vessel, summary, estimate = [p.strip() for p in row.split(" - ")]
    if (berth, vessel, summary) in seen:
        continue
    seen.add((berth, vessel, summary))
    new.append('%s %s %s - %s - %s' % (date, berth, vessel, summary, estimate))
derived = book.rstrip("\n") + "\n" + "\n".join(new) + "\n"
print(json.dumps({"files": {"logbook/claims-2026-09.txt": derived}}))
