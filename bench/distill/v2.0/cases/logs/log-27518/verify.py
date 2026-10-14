# DISTILL-CANARY-99685b69 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/delivery-events.jsonl"].splitlines()

deferred = []
bounced = set()
for line in lines:
    if not line.strip():
        continue
    r = json.loads(line)
    if r["event"] == "deferred":
        deferred.append(r)
    if r["event"] == "bounced":
        bounced.add(r["queue"])

ids = {r["queue"] for r in deferred}
heavy = {r["queue"] for r in deferred if r["attempts"] >= 3}
kept = {q for q in heavy if not any(r["queue"] == q and r["rcpt"].endswith("sandbox.heroncourier.cn") for r in deferred)}
domains = {}
for r in deferred:
    if r["queue"] in kept:
        d = r["rcpt"].split("@")[1]
        domains[d] = domains.get(d, 0) + 1
top = sorted(domains.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

_sabotage_guard = case["files"].get('logs/delivery-events.jsonl', "")
if not _sabotage_guard.splitlines() or _sabotage_guard.splitlines()[0] != '{"ts":"2026-09-26T03:12:44Z","queue":"Q-55208","rcpt":"kai.tan@heroncourier.cn","event":"deferred","attempts":3}':
    raise SystemExit(1)
print(json.dumps({"expected_number": len(ids)}))
