# DISTILL-CANARY-de74c870 : distillation case
import json

case = json.load(open("case.json"))
book = case["files"]["logbook/supply-2026-09.txt"]
note = case["files"]["notes/purchase-2026-09-28.txt"]
rows = [l for l in note.splitlines() if l.strip()]
date = rows[0].split()[1]
keeper = next(l.split()[1] for l in rows if l.startswith("经手"))
new = []
for row in rows[1:]:
    if row.startswith("经手"):
        continue
    f = row.split()
    if f[3] == "已结清":
        new.append("%s %s %s %s %s 经手 %s" % (date, f[0], f[1], f[2], f[3], keeper))
derived = book.rstrip("\n") + "\n" + "\n".join(new) + "\n"
print(json.dumps({"files": {"logbook/supply-2026-09.txt": derived}}))
