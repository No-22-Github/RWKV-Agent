# DISTILL-CANARY-a8869f2e : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

per_day = {}
for name in sorted(entries):
    if not name.startswith("batches/") or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(entries[name])):
        d = row["日期"]
        old = per_day.get(d, (0, 0))
        per_day[d] = (old[0] + int(row["板数"]), old[1] + int(row["金额元"].replace(",", "")))
lines = []
total = [0, 0]
for d in sorted(per_day):
    boards, yuan = per_day[d]
    lines.append(f"{d},{boards},{yuan}")
    total[0] += boards
    total[1] += yuan
lines.append(f"总计,{total[0]},{total[1]}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
