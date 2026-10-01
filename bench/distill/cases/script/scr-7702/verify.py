# DISTILL-CANARY-7e2ad905 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
per_day = {}
for name in sorted(entries):
    if not name.startswith("rooms/") or not name.endswith(".csv"):
        continue
    rows = list(csv.reader(io.StringIO(entries[name])))[1:]
    for row in rows:
        if not row or row[0].startswith("小计"):
            continue
        day, nights, fee = row[0], int(row[2]), int(row[3])
        old = per_day.get(day, (0, 0))
        per_day[day] = (old[0] + nights, old[1] + fee)
lines = []
total_nights = 0
total_fee = 0
for day in sorted(per_day):
    nights, fee = per_day[day]
    lines.append(f"{day},{nights},{fee}")
    total_nights += nights
    total_fee += fee
lines.append(f"合计,{total_nights},{total_fee}")
print(json.dumps({"expected_stdout": "\n".join(lines)}))
