# DISTILL-CANARY-71c9f4b2 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["orders/backlog-2026-09.csv"])))
seen, hangzhou = set(), []
for r in rows:
    if r["city"] != "杭州":
        continue
    key = tuple(sorted(r.items()))
    if key in seen:
        continue
    seen.add(key)
    hangzhou.append(r)
wholesale = [r for r in hangzhou if r["channel"] == "批发"]
counts, qty = {}, {}
for r in wholesale:
    counts[r["customer"]] = counts.get(r["customer"], 0) + 1
    qty[r["customer"]] = qty.get(r["customer"], 0) + int(r["qty"])
top = max(counts, key=lambda c: counts[c])
out = {
    "expected_number": sum(int(r["qty"]) for r in hangzhou),
    "expected_turn_2": sum(int(r["qty"]) for r in wholesale),
    "expected_turn_4": qty[top],
}
print(json.dumps(out))
