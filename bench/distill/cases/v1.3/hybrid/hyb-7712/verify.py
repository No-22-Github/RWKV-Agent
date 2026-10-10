# DISTILL-CANARY-d08b45f7 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["outbound/pallets-2026-09.csv"])))
seen, distinct = set(), []
for r in rows:
    key = tuple(sorted(r.items()))
    if key in seen:
        continue
    seen.add(key)
    distinct.append(r)
out = {
    "expected_number": len(distinct),
    "expected_turn_3": round(sum(float(r["weight_kg"]) for r in distinct), 2),
}
print(json.dumps(out))
