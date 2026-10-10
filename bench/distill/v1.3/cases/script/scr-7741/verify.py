# DISTILL-CANARY-c91140d5 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

per_day = {}
for name in sorted(entries):
    if not name.startswith("dryers/") or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(entries[name])):
        d = row["日期"]
        old = per_day.get(d, (0, 0))
        per_day[d] = (old[0] + 1, old[1] + int(row["茧量斤"]))
lines = []
total = [0, 0]
for d in sorted(per_day):
    times, jin = per_day[d]
    lines.append(f"{d},{times},{jin}")
    total[0] += times
    total[1] += jin
lines.append(f"总计,{total[0]},{total[1]}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
