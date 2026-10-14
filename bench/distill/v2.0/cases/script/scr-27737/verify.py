# DISTILL-CANARY-eee6ba54 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

per_day = {}
for name in sorted(entries):
    if not name.startswith("consignments/") or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(entries[name])):
        d = row["sent_date"]
        old = per_day.get(d, (0, 0))
        per_day[d] = (old[0] + 1, old[1] + int(row["cases"]))
lines = []
total = [0, 0]
for d in sorted(per_day):
    cons, cases = per_day[d]
    lines.append(f"{d},{cons},{cases}")
    total[0] += cons
    total[1] += cases
lines.append(f"TOTAL,{total[0]},{total[1]}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
