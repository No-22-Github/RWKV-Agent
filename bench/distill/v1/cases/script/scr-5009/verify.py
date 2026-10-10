# DISTILL-CANARY-c92d05be : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
shipped = case["files"]
hidden = case["expect"]["run"]["hidden_files"]

sheet = "trips/2026-09.csv"


def pounds(pence):
    return "%d.%02d" % (pence // 100, pence % 100)


rate = {}
for line in shipped["tariffs.yaml"].splitlines():
    key, _, value = line.partition(":")
    rate[key.strip()] = int(value.strip())

rows = []
for text in (shipped[sheet], hidden["trips/2026-10.csv"]):
    rows.extend(csv.DictReader(io.StringIO(text)))

lines = []
total = 0
for row in sorted(rows, key=lambda r: r["departed_at"]):
    fare = int(row["passengers"]) * rate[row["route"]]
    total += fare
    lines.append("%s,%s,%s" % (row["departed_at"], row["route"], pounds(fare)))
lines.append("TOTAL,%s" % pounds(total))

print(json.dumps({
    "expected_stdout": "\n".join(lines),
    "files": {sheet: shipped[sheet]},
}))
