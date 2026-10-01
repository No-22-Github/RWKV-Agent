# DISTILL-CANARY-b1ecc614 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

per_vat = {}
for name in sorted(entries):
    if not name.startswith("vats/") or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(entries[name])):
        vat = row["缸组"]
        old = per_vat.get(vat, (0, 0))
        per_vat[vat] = (old[0] + 1, old[1] + int(row["醋醅克"]))
lines = []
total = [0, 0]
for vat in sorted(per_vat):
    count, grams = per_vat[vat]
    lines.append(f"{vat},{count},{grams}")
    total[0] += count
    total[1] += grams
lines.append(f"总计,{total[0]},{total[1]}")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
