# DISTILL-CANARY-2f8d64b1 : distillation case
import csv
import io
import json
from datetime import date

case = json.load(open("case.json"))
files = case["files"]
hidden = case["expect"]["run"]["hidden_files"]

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

rows = list(csv.DictReader(io.StringIO(files["visits/2026-09.csv"])))
rows += list(csv.DictReader(io.StringIO(hidden["visits/2026-10.csv"])))

lines = []
for row in sorted(rows, key=lambda r: r["visited_on"]):
    day = date.fromisoformat(row["visited_on"])
    lines.append("%s,%s" % (row["visited_on"], WEEKDAYS[day.weekday()]))

print(json.dumps({
    "expected_stdout": "\n".join(lines),
    "files": {"visits/2026-09.csv": files["visits/2026-09.csv"]},
}))
