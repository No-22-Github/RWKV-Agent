# DISTILL-CANARY-acba95de : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

order = []
balance = {}
for name in sorted(entries):
    if not name.startswith("shops/") or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(entries[name])):
        shop = row["商铺"]
        if shop not in balance:
            balance[shop] = 0
            order.append(shop)
        amount = int(row["金额元"])
        balance[shop] += amount if row["类目"] == "销货" else -amount
lines = [f"{shop},{balance[shop]}" for shop in order]

print(json.dumps({"expected_stdout": "\n".join(lines)}))
