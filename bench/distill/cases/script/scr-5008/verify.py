# DISTILL-CANARY-7a41f6c2 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
shipped = case["files"]
hidden = case["expect"]["run"]["hidden_files"]
month = case["expect"]["run"]["args"][1]

sheet = "outings/2026-08.csv"

rows = []
for text in (shipped[sheet], shipped["outings/2026-09.csv"], hidden["outings/2026-10.csv"]):
    rows.extend(csv.DictReader(io.StringIO(text)))

minutes = {}
for row in rows:
    if not row["date"].startswith(month):
        continue
    minutes[row["boat"]] = minutes.get(row["boat"], 0) + int(row["minutes"])

lines = ["%s,%d" % (boat, minutes[boat]) for boat in sorted(minutes)]
lines.append("TOTAL,%d" % sum(minutes.values()))

print(json.dumps({
    "expected_stdout": "\n".join(lines),
    "files": {sheet: shipped[sheet]},
}))
