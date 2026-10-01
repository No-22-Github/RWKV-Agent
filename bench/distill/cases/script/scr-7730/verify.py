# DISTILL-CANARY-6d82e50d : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

def iso(day):
    if "/" in day:
        d, m, y = day.split("/")
        return f"{y}-{m}-{d}"
    return day

per_day = {}
for name in sorted(entries):
    if not name.startswith("takings/") or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(entries[name])):
        key = iso(row["sale_date"])
        per_day[key] = per_day.get(key, 0) + int(row["pence"])
lines = []
total = 0
for day in sorted(per_day):
    if day.startswith("2026-07"):
        lines.append(f"{day},{per_day[day]}")
        total += per_day[day]
lines.append(f"TOTAL,{total}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
