# DISTILL-CANARY-f2e2b586 : distillation case
import json
from datetime import datetime

case = json.load(open("case.json"))
lines = case["files"]["logs/payments-0925.jsonl"].splitlines()


def ts(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


declines = []
for line in lines:
    if not line.strip():
        continue
    row = json.loads(line)
    if row.get("result") == "declined":
        declines.append(row)

w1 = {r["txn"] for r in declines if ts("2026-09-25T09:00:00Z") <= ts(r["ts"]) < ts("2026-09-25T12:00:00Z")}
w2 = {r["txn"] for r in declines if ts("2026-09-25T12:00:00Z") <= ts(r["ts"]) < ts("2026-09-25T15:00:00Z")}
gateways = {}
for r in declines:
    if r["txn"] in w1:
        gateways[r["gateway"]] = gateways.get(r["gateway"], 0) + 1
top = sorted(gateways.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

forms = [
    "%d declined" % len(w1), "%d transactions" % len(w1), "%d declines" % len(w1),
    top,
    "%d declined" % len(w2), "%d transactions" % len(w2), "%d declines" % len(w2),
]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
