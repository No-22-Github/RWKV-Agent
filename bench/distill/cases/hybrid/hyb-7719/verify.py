# DISTILL-CANARY-6c25ae93 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["bookings/cancellations-2026.csv"])))
seen, clean = set(), []
for r in rows:
    key = tuple(sorted(r.items()))
    if key in seen:
        continue
    seen.add(key)
    clean.append(r)
october = [r for r in clean if r["cancel_date"].startswith("2026-10")]
sep = [r for r in clean if r["cancel_date"].startswith("2026-09")]
causes = {}
for r in sep:
    causes[r["cause"]] = causes.get(r["cause"], 0) + 1
top = max(causes, key=lambda c: causes[c])
out = {
    "expected_number": len(october),
    "expected_turn_2": len(sep),
    "expected_turn_4": sum(1 for r in october if r["cause"] == top),
}
print(json.dumps(out))
