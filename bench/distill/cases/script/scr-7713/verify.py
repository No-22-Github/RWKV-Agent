# DISTILL-CANARY-4a462ab4 : distillation case
import csv
import io
import json

def build_stdout(entries):
    per = {}
    for name in sorted(entries):
        if not name.startswith("feeds/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            cell = row["grams"].strip()
            if cell == "":
                continue
            tank = row["tank"]
            per[tank] = per.get(tank, 0) + int(cell)
    lines = []
    total = 0
    for tank in sorted(per):
        lines.append(f"{tank},{per[tank]}")
        total += per[tank]
    lines.append(f"TOTAL,{total}")
    return "\n".join(lines)

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
