# DISTILL-CANARY-a49d3673 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

per_day = {}
for name in sorted(entries):
    if not name.startswith("sessions/") or not name.endswith(".csv"):
        continue
    if "/" in name[len("sessions/"):]:
        continue
    for row in csv.DictReader(io.StringIO(entries[name])):
        day = row["session_date"]
        old = per_day.get(day, (0, 0))
        per_day[day] = (old[0] + 1, old[1] + int(row["pence"]))
lines = []
total = [0, 0]
for day in sorted(per_day):
    count, pence = per_day[day]
    lines.append(f"{day},{count},{pence}")
    total[0] += count
    total[1] += pence
lines.append(f"TOTAL,{total[0]},{total[1]}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
