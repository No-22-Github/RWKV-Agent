# DISTILL-CANARY-47a91a39 : distillation case
import csv
import io
import json

def build_stdout(entries):
    per_file = {}
    for name in sorted(entries):
        base = name.rsplit("/", 1)[-1]
        if not name.startswith("downloads/") or not base.startswith("reservations-"):
            continue
        month = base[len("reservations-"):-len(".csv")]
        days = {}
        for row in csv.DictReader(io.StringIO(entries[name])):
            days[row["day"]] = days.get(row["day"], 0) + 1
        per_file[month] = days
    newest = max(per_file)
    lines = []
    total = 0
    for day in sorted(per_file[newest]):
        lines.append(f"{day},{per_file[newest][day]}")
        total += per_file[newest][day]
    lines.append(f"TOTAL,{total}")
    return "\n".join(lines)

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
