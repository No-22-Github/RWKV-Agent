# DISTILL-CANARY-97c14508 : distillation case
import csv
import io
import json

def build_stdout(entries):
    case = json.load(open("case.json", encoding="utf-8"))
    n = int(case["expect"]["run"]["args"][1])
    per = {}
    for name in sorted(entries):
        if not name.startswith("bills/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            cat = row["品类"]
            per[cat] = per.get(cat, 0) + int(row["碗数"])
    ranked = sorted(per.items(), key=lambda kv: -kv[1])
    lines = [f"{cat},{bowls}" for cat, bowls in ranked[:n]]
    return "\n".join(lines)

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
