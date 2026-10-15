# EXAM-CANARY-c3f81b94 : exam gap-fill case
import json, re, csv, io
case = json.load(open("case.json", encoding="utf-8"))
rows = list(csv.reader(io.StringIO(case["files"]["returns-log.csv"])))
assert rows[0] == ["date", "store", "sku", "qty", "unit_price", "type"]
c = {}
for r in rows[1:]:
    if "2026-07-01" <= r[0] <= "2026-09-30" and r[5] == "return":
        c[r[1]] = c.get(r[1], 0) + 1
best = sorted(c.items(), key=lambda kv: -kv[1])
assert best[0][1] > best[1][1]
print(json.dumps({"expected_contains_any": [best[0][0], best[0][0].split()[0]]}))
