# DISTILL-CANARY-91c47e2b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["metrics/incidents-2026-09.csv"])))
seen, clean = set(), []
for r in rows:
    key = tuple(sorted(r.items()))
    if key in seen:
        continue
    seen.add(key)
    clean.append(r)
prod = [r for r in clean if r["env"] == "production"]
out = {
    "expected_number": len(clean),
    "expected_turn_2": len(prod),
}
print(json.dumps(out))
