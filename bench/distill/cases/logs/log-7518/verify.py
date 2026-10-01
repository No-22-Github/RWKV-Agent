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

forms = ["%d messages" % len(ids), "%d deferred" % len(ids),
         "%d messages" % len(heavy), "%d deferred" % len(heavy),
         "%d messages" % len(kept), "%d deferred" % len(kept),
         top,
         "%d messages" % len(bounced), "%d bounced" % len(bounced)]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
