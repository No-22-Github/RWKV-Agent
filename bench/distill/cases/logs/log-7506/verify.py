# DISTILL-CANARY-34717af9 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/smtp-delivery.log"].splitlines()

window = 0
day = 0
for line in lines:
    if not line.strip():
        continue
    f = line.split()
    ts = f[0] + " " + f[1]
    if "status=deferred" not in line:
        continue
    day += 1
    if "2026-09-24 08:00:00" <= ts < "2026-09-24 09:00:00":
        window += 1

forms = ["%d 封" % window, "%d 封" % day]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
