# DISTILL-CANARY-64f855f2 : distillation case
import json
import re

case = json.load(open("case.json"))
book = case["files"]["logs/runtime.log"]
sheet = case["files"]["notes/meter-2026-09-27.txt"]
rows = [l for l in sheet.splitlines() if l.strip()]
m = re.search(r"(\d{4}-\d{2}-\d{2})", rows[0])
if not m:
    raise SystemExit("meter sheet header has no date")
date = m.group(1)
operator = next(l.split("operator", 1)[1].strip() for l in rows if l.startswith("operator"))
reading = rows[1].strip()
line = "%s %s - operator %s" % (date, reading, operator)
derived = book.rstrip("\n") + "\n" + line + "\n"
print(json.dumps({"files": {"logs/runtime.log": derived}}))
