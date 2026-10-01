# DISTILL-CANARY-342a4259 : distillation case
import csv
import io
import json

def build_stdout(entries):
    per = {}
    for name in sorted(entries):
        if not name.startswith("swaps/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            cell = row["bikes"].strip()
            if cell == "":
                continue
            station = row["station"]
            per[station] = per.get(station, 0) + int(cell)
    lines = []
    total = 0
    for station in sorted(per):
        lines.append(f"{station},{per[station]}")
        total += per[station]
    lines.append(f"TOTAL,{total}")
    return "\n".join(lines)

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
