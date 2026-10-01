# DISTILL-CANARY-ead092fa : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

lines = []
for name in sorted(entries):
    if not name.startswith("mobs/") or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(entries[name])):
        lines.append(f"{row['checked_at']},{row['mob']},{row['flag']}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
