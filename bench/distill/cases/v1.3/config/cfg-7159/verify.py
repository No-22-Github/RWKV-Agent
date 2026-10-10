# DISTILL-CANARY-92b38d61 : distillation case
import json
import re

case = json.load(open("case.json"))
book = case["files"]["logs/repair-2026-09.txt"]
sheet = case["files"]["sheets/工单-2026-09-29.txt"]
rows = [l for l in sheet.splitlines() if l.strip()]
m = re.search(r"(\d{4}-\d{2}-\d{2})", rows[0])
if not m:
    raise SystemExit("工单表头没有日期")
date = m.group(1)
new = []
for row in rows[1:]:
    f = row.split()
    if f[2] == "完成":
        new.append("%s %s %s %s %s" % (date, f[0], f[1], f[2], f[3]))
derived = book.rstrip("\n") + "\n" + "\n".join(new) + "\n"
print(json.dumps({"files": {"logs/repair-2026-09.txt": derived}}))
