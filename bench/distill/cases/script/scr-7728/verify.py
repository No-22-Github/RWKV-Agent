# DISTILL-CANARY-3805b211 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

seen = set()
per_day = {}
for name in sorted(entries):
    if not name.startswith("shearings/") or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(entries[name])):
        pid = row["pickup_id"]
        if pid in seen:
            continue
        seen.add(pid)
        day = row["pickup_date"]
        old = per_day.get(day, (0, 0))
        per_day[day] = (old[0] + 1, old[1] + int(row["kg"]))
lines = []
total = [0, 0]
for day in sorted(per_day):
    pickups, kg = per_day[day]
    lines.append(f"{day},{pickups},{kg}")
    total[0] += pickups
    total[1] += kg
lines.append(f"TOTAL,{total[0]},{total[1]}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
