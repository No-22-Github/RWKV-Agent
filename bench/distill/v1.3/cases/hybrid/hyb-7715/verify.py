# DISTILL-CANARY-7d2e91a4 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["jobs/print-jobs-2026-09.csv"])))
seen, rush = set(), []
for r in rows:
    if r["rush"] != "是":
        continue
    key = tuple(sorted(r.items()))
    if key in seen:
        continue
    seen.add(key)
    rush.append(r)
top = max(rush, key=lambda r: float(r["total_yuan"]))
out = {
    "expected_number": round(sum(float(r["total_yuan"]) for r in rush), 2),
    "expected_turn_3": float(top["total_yuan"]),
}
print(json.dumps(out))
