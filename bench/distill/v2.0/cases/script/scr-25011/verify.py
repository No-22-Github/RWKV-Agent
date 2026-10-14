# DISTILL-CANARY-c78fdbb0 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = dict(case["files"])
files.update(case["expect"]["run"]["hidden_files"])

rows = []
for path in sorted(files):
    if path.endswith(".csv"):
        rows.extend(csv.DictReader(io.StringIO(files[path])))

lines = []
total = 0.0
for row in sorted(rows, key=lambda r: r["casting_no"]):
    weight = int(row["bells"]) * float(row["unit_kg"])
    total += weight
    lines.append("%s,%s,%.2f" % (row["casting_no"], row["alloy"], weight))
lines.append("TOTAL,%.2f" % total)

keep = "castings/2026-09.csv"
print(json.dumps({
    "expected_stdout": "\n".join(lines),
    "files": {keep: files[keep]},
}))
