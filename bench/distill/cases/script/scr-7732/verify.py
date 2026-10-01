# DISTILL-CANARY-2609375f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

picks = {}
counts = {}
returns = {}
for name in sorted(entries):
    if name.startswith("pickers/") and name.endswith(".csv"):
        for row in csv.DictReader(io.StringIO(entries[name])):
            d = row["pick_date"]
            picks[d] = picks.get(d, 0) + int(row["kg"])
            counts[d] = counts.get(d, 0) + 1
    elif name.startswith("returns/") and name.endswith(".csv"):
        for row in csv.DictReader(io.StringIO(entries[name])):
            d = row["return_date"]
            returns[d] = returns.get(d, 0) + int(row["kg"])
lines = []
total = [0, 0]
for d in sorted(set(picks) | set(returns)):
    c = counts.get(d, 0)
    net = picks.get(d, 0) - returns.get(d, 0)
    lines.append(f"{d},{c},{net}")
    total[0] += c
    total[1] += net
lines.append(f"TOTAL,{total[0]},{total[1]}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
