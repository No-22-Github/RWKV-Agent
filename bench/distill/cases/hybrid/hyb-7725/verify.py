# DISTILL-CANARY-47b0e98f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["orders/parts-2026-09.csv"])))
seen, clean = set(), []
for r in rows:
    key = tuple(sorted(r.items()))
    if key in seen:
        continue
    seen.add(key)
    clean.append(r)
prov = [r for r in clean if r["region"] == "省内"]
kept = [r for r in prov if r["order_id"] != "PO-7718"]
top = max(kept, key=lambda r: float(r["amount_yuan"]))
out = {
    "expected_number": round(sum(float(r["amount_yuan"]) for r in clean), 2),
    "expected_turn_2": round(sum(float(r["amount_yuan"]) for r in prov), 2),
    "expected_turn_3": round(sum(float(r["amount_yuan"]) for r in kept), 2),
    "expected_turn_5": float(top["amount_yuan"]),
}
print(json.dumps(out))
