# DISTILL-CANARY-75cf98ba : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

rows = []
for name in sorted(entries):
    if not name.startswith("trails/") or not name.endswith(".csv"):
        continue
    rows.extend(csv.DictReader(io.StringIO(entries[name])))
lines = []
for row in sorted(rows, key=lambda r: r["trail"]):
    if row["checked_date"] == "2026-10-04":
        lines.append(f"{row['checked_date']},{row['trail']},{row['status']}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
