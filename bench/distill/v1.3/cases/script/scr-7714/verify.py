# DISTILL-CANARY-61f43d51 : distillation case
import csv
import io
import json

def build_stdout(entries):
    per = {}
    for name in sorted(entries):
        if not name.startswith("slips/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            cell = row["件数"].strip()
            pieces = 0 if cell in ("", "-") else int(cell)
            cat = row["品类"]
            per[cat] = per.get(cat, 0) + pieces
    lines = []
    total = 0
    for cat in sorted(per):
        lines.append(f"{cat},{per[cat]}")
        total += per[cat]
    lines.append(f"合计,{total}")
    return "\n".join(lines)

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
