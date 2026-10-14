# DISTILL-CANARY-e44b5de6 : distillation case
import json

case = json.load(open("case.json"))
book = case["files"]["logbook/claims-2026-09.txt"]
sheet = case["files"]["notices/inspector-2026-09-30.txt"]
rows = [l for l in sheet.splitlines() if l.strip()]
date = rows[0].split()[-1]
berth, vessel, summary, estimate = [p.strip() for p in rows[1].split(" - ")]
line = '%s %s %s - %s - %s' % (date, berth, vessel, summary, estimate)
derived = book.rstrip("\n") + "\n" + line + "\n"
print(json.dumps({"files": {"logbook/claims-2026-09.txt": derived}}))
