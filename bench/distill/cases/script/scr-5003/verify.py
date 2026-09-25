# DISTILL-CANARY-a1d0f8c6 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
hidden = case["expect"]["run"]["hidden_files"]

rows = list(csv.DictReader(io.StringIO(files["sessions/2026-09.csv"])))
rows += list(csv.DictReader(io.StringIO(hidden["sessions/2026-10.csv"])))

lines = []
total = 0
for row in sorted(rows, key=lambda r: r["date"]):
    total += int(row["attendees"])
    lines.append("%s,%s" % (row["date"], row["attendees"]))
lines.append("TOTAL,%d" % total)

print(json.dumps({
    "expected_stdout": "\n".join(lines),
    "files": {"sessions/2026-09.csv": files["sessions/2026-09.csv"]},
}))
