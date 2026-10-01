# DISTILL-CANARY-2bcd0a68 : distillation case
import csv
import io
import json

def build_stdout(entries):
    per = {}
    for name in sorted(entries):
        if not name.startswith("intake/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            if row["状态"] != "入库":
                continue
            stall = row["摊位"]
            per[stall] = per.get(stall, 0) + int(row["件数"])
    lines = []
    total = 0
    for stall in sorted(per):
        lines.append(f"{stall},{per[stall]}")
        total += per[stall]
    lines.append(f"合计,{total}")
    return "\n".join(lines)

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
