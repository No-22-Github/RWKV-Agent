# DISTILL-CANARY-ec2f170d : distillation case
import csv
import io
import json

def build_stdout(entries):
    per = {}
    for name in sorted(entries):
        if not name.startswith("hives/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            cell = row["frames"].strip()
            if not cell.isdigit():
                continue
            hive = row["hive"]
            per[hive] = per.get(hive, 0) + int(cell)
    lines = []
    total = 0
    for hive in sorted(per):
        lines.append(f"{hive},{per[hive]}")
        total += per[hive]
    lines.append(f"TOTAL,{total}")
    return "\n".join(lines)

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
