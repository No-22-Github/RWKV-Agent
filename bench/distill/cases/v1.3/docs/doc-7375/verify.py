# DISTILL-CANARY-9e6e133c : distillation case
import json
import re

case = json.load(open("case.json"))
book = case["files"]["ledger/dispensed-2026-09.txt"]
sheet = case["files"]["notes/scripts-2026-09-28.txt"]
rows = [l for l in sheet.splitlines() if l.strip()]
m = re.search(r"(\d{4}-\d{2}-\d{2})", rows[0])
if not m:
    raise SystemExit("dispensing sheet header has no date")
date = m.group(1)
vet = rows[0].rsplit("-", 1)[1].strip()
new = []
for row in rows[1:]:
    patient, rest = row.split(":", 1)
    item, route = [p.strip() for p in rest.rsplit("-", 1)]
    if route == "dispensary":
        new.append("%s %s - %s - dispensed - %s" % (date, patient.strip(), item, vet))
derived = book.rstrip("\n") + "\n" + "\n".join(new) + "\n"
print(json.dumps({"files": {"ledger/dispensed-2026-09.txt": derived}}))
