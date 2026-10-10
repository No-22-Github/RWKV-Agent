# DISTILL-CANARY-6c32364c : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

per_bed = {}
for name in sorted(entries):
    if not name.startswith("pickers/") or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(entries[name])):
        bed = row["bed"]
        old = per_bed.get(bed, (0, 0))
        per_bed[bed] = (old[0] + 1, old[1] + int(row["kg"]))
lines = []
total = [0, 0]
for bed in sorted(per_bed):
    sacks, kg = per_bed[bed]
    lines.append(f"{bed},{sacks},{kg}")
    total[0] += sacks
    total[1] += kg
lines.append(f"TOTAL,{total[0]},{total[1]}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
