# DISTILL-CANARY-e17b5839 : distillation case
import json

case = json.load(open("case.json"))
book = case["files"]["logbook/receiving-2026-09.txt"]
note = case["files"]["notes/delivery-DH-2210.txt"]
lines = [line for line in note.splitlines() if line.strip()]
head = lines[0].split()
carrier, number = head[0], head[2]
arrival_date = next(l.split()[1] for l in lines if l.startswith("到店日期"))
items = []
in_items = False
for line in lines:
    if line.startswith("品名"):
        in_items = True
        continue
    if in_items and "正常入库" in line:
        fields = line.split()
        items.append(f"{arrival_date} 到货 {fields[0]} {fields[1]} {carrier} {number}")
derived = book.rstrip("\n") + "\n" + "\n".join(items) + "\n"
print(json.dumps({"files": {"logbook/receiving-2026-09.txt": derived}}))
