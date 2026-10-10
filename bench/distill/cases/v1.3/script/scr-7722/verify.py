# DISTILL-CANARY-dcd87b3a : distillation case
import csv
import io
import json

def build_stdout(entries):
    per = {}
    for name in sorted(entries):
        if not name.startswith("tills/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            kind = row["kind"]
            if kind == "training":
                continue
            day = row["entry_on"]
            pence = int(row["pence"])
            if kind == "refund":
                pence = -pence
            per[day] = per.get(day, 0) + pence
    lines = []
    total = 0
    for day in sorted(per):
        lines.append(f"{day},{per[day]}")
        total += per[day]
    lines.append(f"TOTAL,{total}")
    return "\n".join(lines)

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
