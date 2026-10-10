# DISTILL-CANARY-36ce2ae5 : distillation case
import csv
import io
import json

def build_stdout(entries):
    per = {}
    for name in sorted(entries):
        if not name.startswith("stock/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            cell = row["盒数"].strip()
            boxes = 0 if cell in ("", "-", "缺卡") else int(cell)
            cat = row["品类"]
            per[cat] = per.get(cat, 0) + boxes
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
