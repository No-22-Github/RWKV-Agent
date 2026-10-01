# DISTILL-CANARY-1b2b3fcc : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

per_bar = {}
for name in sorted(entries):
    if not name.startswith("bars/") or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(entries[name])):
        bar = row["bar"]
        pence = int(row["takings_pence"].replace(",", ""))
        old = per_bar.get(bar, (0, 0))
        per_bar[bar] = (old[0] + 1, old[1] + pence)
lines = []
total = [0, 0]
for bar in sorted(per_bar):
    sales, pence = per_bar[bar]
    lines.append(f"{bar},{sales},{pence}")
    total[0] += sales
    total[1] += pence
lines.append(f"TOTAL,{total[0]},{total[1]}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
