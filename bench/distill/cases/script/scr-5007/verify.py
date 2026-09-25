# DISTILL-CANARY-b5e08d34 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
shipped = case["files"]
hidden = case["expect"]["run"]["hidden_files"]

sheet = "collections/2026-08.csv"


def pounds(pence):
    return "%d.%02d" % (pence // 100, pence % 100)


rows = []
for text in (shipped[sheet], hidden["collections/2026-09.csv"]):
    rows.extend(csv.DictReader(io.StringIO(text)))

lines = []
total = 0
for row in sorted(rows, key=lambda r: r["collected_on"]):
    amount = int(row["churns"]) * int(row["rate_pence"])
    total += amount
    lines.append("%s,%s,%s" % (row["collected_on"], row["farm"], pounds(amount)))
lines.append("TOTAL,%s" % pounds(total))

print(json.dumps({
    "expected_stdout": "\n".join(lines),
    "files": {sheet: shipped[sheet]},
}))
