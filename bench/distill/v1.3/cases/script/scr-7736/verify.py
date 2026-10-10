# DISTILL-CANARY-6c4ee502 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

seen = set()
per_day = {}
for name in sorted(entries):
    if not name.startswith("batches/") or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(entries[name])):
        bid = row["batch_id"]
        if bid == "BATCH TOTAL":
            continue
        if bid in seen:
            continue
        seen.add(bid)
        day = row["made_date"]
        old = per_day.get(day, (0, 0))
        per_day[day] = (old[0] + 1, old[1] + int(row["shell_kg"]))
lines = []
total = [0, 0]
for day in sorted(per_day):
    batches, shell = per_day[day]
    lines.append(f"{day},{batches},{shell}")
    total[0] += batches
    total[1] += shell
lines.append(f"TOTAL,{total[0]},{total[1]}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
