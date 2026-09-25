# DISTILL-CANARY-745c7321 : distillation case
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
reels = 0
kg = 0
for row in sorted(rows, key=lambda r: r["run_date"]):
    reels += int(row["reels"])
    kg += int(row["kg"])
    lines.append("%s,%s,%d,%d" % (row["run_date"], row["beater"], int(row["reels"]), int(row["kg"])))
lines.append("TOTAL,%d,%d" % (reels, kg))

keep = "beats/2026-09.csv"
print(json.dumps({
    "expected_stdout": "\n".join(lines),
    "files": {keep: files[keep]},
}))
