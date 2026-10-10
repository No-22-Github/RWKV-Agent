# DISTILL-CANARY-bdd4a38c : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

per_day = {}
for name in sorted(entries):
    if not name.startswith("casks/") or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(entries[name])):
        day = row["char_date"]
        raw = row["minutes"].strip()
        minutes = int(raw) if raw else 0
        old = per_day.get(day, (0, 0))
        per_day[day] = (old[0] + minutes, old[1] + int(row["pence"]))
lines = []
total = [0, 0]
for day in sorted(per_day):
    minutes, pence = per_day[day]
    lines.append(f"{day},{minutes},{pence}")
    total[0] += minutes
    total[1] += pence
lines.append(f"TOTAL,{total[0]},{total[1]}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
