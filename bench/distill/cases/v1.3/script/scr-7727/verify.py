# DISTILL-CANARY-8ab75739 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

per_pit = {}
for name in sorted(entries):
    if not name.startswith("casks/") or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(entries[name])):
        pit = row["pit"]
        old = per_pit.get(pit, (0, 0))
        per_pit[pit] = (old[0] + 1, old[1] + int(row["minutes"]))
lines = []
total = [0, 0]
for pit in sorted(per_pit):
    firings, minutes = per_pit[pit]
    lines.append(f"{pit},{firings},{minutes}")
    total[0] += firings
    total[1] += minutes
lines.append(f"TOTAL,{total[0]},{total[1]}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
