# DISTILL-CANARY-1fb56a11 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["exports/pump-outs-may.csv"]))
done = []
voids = 0
berths = {}
for r in rows:
    sid = (r.get("service_id") or "").strip()
    if sid == "TOTAL":
        continue
    status = (r.get("status") or "").strip()
    if status == "done":
        done.append(r)
        berth = (r.get("berth") or "").strip()
        berths[berth] = berths.get(berth, 0) + 1
    elif status == "void":
        voids += 1
if not done:
    raise SystemExit(1)
top = max(sorted(berths), key=lambda b: berths[b])
facts = [
    "%d pump-outs" % len(done),
    top,
    "%d void bookings" % voids,
]
print(json.dumps({"expected_contains_any": facts}))
