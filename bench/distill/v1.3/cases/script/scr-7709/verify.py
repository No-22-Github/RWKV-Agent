# DISTILL-CANARY-2f283924 : distillation case
import csv
import io
import json

def build_stdout(entries):
    seen = set()
    per = {}
    for name in sorted(entries):
        if not name.startswith("sowings/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            bid = row["batch_id"]
            if bid in seen:
                continue
            seen.add(bid)
            sown = row["sown_on"]
            if "/" in sown:
                d, m, y = sown.split("/")
                day = f"{y}-{int(m):02d}-{int(d):02d}"
            else:
                day = sown
            per[day] = per.get(day, 0) + int(row["trays"])
    lines = []
    total = 0
    for day in sorted(per):
        lines.append(f"{day},{per[day]}")
        total += per[day]
    lines.append(f"SEASON,{total}")
    return "\n".join(lines)

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
