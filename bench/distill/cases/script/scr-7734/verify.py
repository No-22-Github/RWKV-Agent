# DISTILL-CANARY-168565d5 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

per_day = {}
for name in sorted(entries):
    if (name.startswith("gates/") or name.startswith("huts/")) and name.endswith(".csv"):
        for row in csv.DictReader(io.StringIO(entries[name])):
            d = row["date"]
            per_day[d] = per_day.get(d, 0) + int(row["rides"])
lines = [f"{d},{per_day[d]}" for d in sorted(per_day)]
lines.append(f"TOTAL,{sum(per_day.values())}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
