# DISTILL-CANARY-3ea08d56 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["sales/store-daily-2026-09.csv"])))
seen, clean = set(), []
for r in rows:
    key = tuple(sorted(r.items()))
    if key in seen:
        continue
    seen.add(key)
    clean.append(r)
kept = [r for r in clean if not (r["store"] == "梅陇店" and r["date"] in ("2026-09-13", "2026-09-26"))]
out = {
    "expected_number": round(sum(float(r["amount_yuan"]) for r in clean), 2),
    "expected_turn_2": round(sum(float(r["amount_yuan"]) for r in kept), 2),
    "expected_turn_4": round(sum(float(r["amount_yuan"]) for r in clean if r["store"] == "桂花里店"), 2),
}
print(json.dumps(out))
