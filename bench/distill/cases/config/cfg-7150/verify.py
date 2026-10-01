# DISTILL-CANARY-2e218e1b : distillation case
import json
import re

case = json.load(open("case.json"))
book = case["files"]["logs/service.log"]
sheet = case["files"]["notes/ticket-2026-09-28.txt"]
rows = [l for l in sheet.splitlines() if l.strip()]
m = re.search(r"(\d{4}-\d{2}-\d{2})", rows[0])
if not m:
    raise SystemExit("ticket sheet header has no date")
date = m.group(1)
operator = rows[0].split("operator", 1)[1].strip()
new = []
for row in rows[1:]:
    left, right = [p.strip() for p in row.split(" - ")]
    if not right.startswith("completed"):
        continue
    slip = left.split()[1]
    boat = left.split()[2]
    gal = left.split()[3]
    new.append('%s %s PUMPOUT slip %s %s %s gal COMPLETE operator %s'
               % (date, right.split()[1], slip, boat, gal, operator))
derived = book.rstrip("\n") + "\n" + "\n".join(new) + "\n"
print(json.dumps({"files": {"logs/service.log": derived}}))
