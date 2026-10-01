# DISTILL-CANARY-b8fee867 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
entries = dict(case["files"])
entries.update(case["expect"]["run"]["hidden_files"])

rows = []
for name in sorted(entries):
    if not name.startswith("vats/") or not name.endswith(".csv"):
        continue
    rows.extend(csv.DictReader(io.StringIO(entries[name])))
picked = sorted((r for r in rows if r["缸组"] == "西缸组"), key=lambda r: r["日期"])
lines = [f"{r['日期']},{r['缸组']},{r['醋醅克']}" for r in picked]
lines.append(f"西缸组：小计 {sum(int(r['醋醅克']) for r in picked)} 克")

print(json.dumps({"expected_stdout": "\n".join(lines)}))
