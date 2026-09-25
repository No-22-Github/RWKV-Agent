# DISTILL-CANARY-3f7a2c91 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
shipped = case["files"]
hidden = case["expect"]["run"]["hidden_files"]

sheet = "crossings/2026-09.csv"


def pounds(pence):
    return "%d.%02d" % (pence // 100, pence % 100)


rows = []
for text in (shipped[sheet], hidden["crossings/2026-10.csv"]):
    rows.extend(csv.DictReader(io.StringIO(text)))

lines = []
total = 0
for row in sorted(rows, key=lambda r: r["sailed_on"]):
    fare = int(row["vehicles"]) * int(row["fare_pence"])
    total += fare
    lines.append("%s,%s,%s" % (row["sailed_on"], row["route"], pounds(fare)))
lines.append("TOTAL,%s" % pounds(total))

print(json.dumps({
    "expected_stdout": "\n".join(lines),
    "files": {sheet: shipped[sheet]},
}))
