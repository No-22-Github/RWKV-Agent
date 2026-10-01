# DISTILL-CANARY-a2a7ecbf : distillation case
import csv
import io
import json

def build_stdout(entries):
    case = json.load(open("case.json", encoding="utf-8"))
    since = case["expect"]["run"]["args"][1]

    def norm(s):
        if "/" in s:
            d, m, y = s.split("/")
            return f"{y}-{int(m):02d}-{int(d):02d}"
        return s

    per = {}
    for name in sorted(entries):
        if not name.startswith("pledges/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            day = norm(row["logged_on"])
            per[day] = per.get(day, 0) + int(row["pledge_pence"])
    lines = []
    total = 0
    for day in sorted(per):
        if day < since:
            continue
        lines.append(f"{day},{per[day]}")
        total += per[day]
    lines.append(f"TOTAL,{total}")
    return "\n".join(lines)

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
