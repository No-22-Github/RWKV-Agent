# DISTILL-CANARY-c85e41b2 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
days = {}
for name in sorted(entries):
    if not name.startswith("batches/") or not name.endswith(".csv"):
        continue
    for row in list(csv.reader(io.StringIO(entries[name])))[1:]:
        if not row:
            continue
        day, green, roasted = row[0], int(row[2]), int(row[3])
        old = days.get(day, (0, 0))
        days[day] = (old[0] + green, old[1] + roasted)
lines = []
total_green = 0
total_roasted = 0
for day in sorted(days):
    green, roasted = days[day]
    lines.append(f"{day},{green},{roasted}")
    total_green += green
    total_roasted += roasted
lines.append(f"TOTAL,{total_green},{total_roasted}")
print(json.dumps({"expected_stdout": "\n".join(lines)}))
