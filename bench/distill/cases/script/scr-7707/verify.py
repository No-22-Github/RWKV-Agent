# DISTILL-CANARY-219351ed : distillation case
import csv
import io
import json

def build_stdout(entries):
    per = {}
    for name in sorted(entries):
        if not name.startswith("orders/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            variety = row["variety"]
            ordered, refunded = int(row["ordered"]), int(row["refunded"])
            per[variety] = per.get(variety, 0) + ordered - refunded
    lines = []
    total = 0
    for variety in sorted(per):
        lines.append(f"{variety},{per[variety]}")
        total += per[variety]
    lines.append(f"NET,{total}")
    return "\n".join(lines)

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
