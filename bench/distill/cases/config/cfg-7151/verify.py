# DISTILL-CANARY-edd05a71 : distillation case
import json
import re

case = json.load(open("case.json"))
book = case["files"]["logs/patrol.log"]
sheet = case["files"]["sheets/round-2026-09-29.txt"]
rows = [l for l in sheet.splitlines() if l.strip()]
m = re.search(r"(\d{4}-\d{2}-\d{2})", rows[0])
if not m:
    raise SystemExit("round sheet header has no date")
date = m.group(1)
new = []
seen = set()
for row in rows[1:]:
    if (row, date) in seen:
        continue
    seen.add((row, date))
    new.append("%s %s" % (date, row))
derived = book.rstrip("\n") + "\n" + "\n".join(new) + "\n"
print(json.dumps({"files": {"logs/patrol.log": derived}}))
