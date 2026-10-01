# DISTILL-CANARY-795d05e9 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])
total = 0
for name in sorted(entries):
    if not name.startswith("pressings/") or not name.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(entries[name])):
        total += int(row["bottles"])
print(json.dumps({"expected_stdout": f"GRAND,{total}"}))
