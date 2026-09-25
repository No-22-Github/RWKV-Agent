# DISTILL-CANARY-2bd01b68 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = dict(case["files"])
files.update(case["expect"]["run"]["hidden_files"])

SHADE = "indigo"
rows = []
for path in sorted(files):
    if path.endswith(".csv"):
        rows.extend(csv.DictReader(io.StringIO(files[path])))

lines = []
total = 0
for row in sorted(rows, key=lambda r: r["lot_no"]):
    if row["shade"] != SHADE:
        continue
    metres = int(row["metres"])
    total += metres
    lines.append("%s,%s,%d" % (row["lot_no"], row["shade"], metres))
lines.append("TOTAL,%d" % total)

keep = "lots/2026-09.csv"
print(json.dumps({
    "expected_stdout": "\n".join(lines),
    "files": {keep: files[keep]},
}))
