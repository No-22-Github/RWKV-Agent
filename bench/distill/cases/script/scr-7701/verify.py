# DISTILL-CANARY-b3f19c47 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
per_day = {}
for name in sorted(entries):
    if not name.startswith("ledgers/") or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(entries[name])):
        day = row["booked_on"]
        old = per_day.get(day, (0, 0))
        per_day[day] = (old[0] + 1, old[1] + int(row["pence"]))
lines = []
total_bookings = 0
total_pence = 0
for day in sorted(per_day):
    bookings, pence = per_day[day]
    lines.append(f"{day},{bookings},{pence}")
    total_bookings += bookings
    total_pence += pence
lines.append(f"TOTAL,{total_bookings},{total_pence}")
print(json.dumps({"expected_stdout": "\n".join(lines)}))
