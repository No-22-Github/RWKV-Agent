# DISTILL-CANARY-aea59948 : distillation case
import csv
import io
import json

def build_stdout(entries):
    case = json.load(open("case.json", encoding="utf-8"))
    plot_want = case["expect"]["run"]["args"][1]
    per = {}
    for name in sorted(entries):
        if not name.startswith("readings/") or not name.endswith(".csv"):
            continue
        for row in csv.DictReader(io.StringIO(entries[name])):
            plot = row["plot"]
            per[plot] = per.get(plot, 0) + int(row["litres"])
    return f"{plot_want},{per[plot_want]}"

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
print(json.dumps({"expected_stdout": build_stdout(entries)}))
