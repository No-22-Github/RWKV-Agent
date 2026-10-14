# DISTILL-CANARY-19e34837 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

per_day = {}
for name in sorted(entries):
    if not name.startswith("intakes/") or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(entries[name])):
        d = row["日期"]
        old = per_day.get(d, (0, 0, 0))
        per_day[d] = (old[0] + 1, old[1] + int(row["茧量斤"]), old[2] + int(row["元"]))
lines = []
total = [0, 0, 0]
for d in sorted(per_day):
    n, jin, yuan = per_day[d]
    lines.append(f"{d},{n},{jin},{yuan}")
    total[0] += n
    total[1] += jin
    total[2] += yuan
lines.append(f"总计,{total[0]},{total[1]},{total[2]}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
