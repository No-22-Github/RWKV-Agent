# DISTILL-CANARY-30d74b8b : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/edge-access.log"].splitlines()

window = 0
gateway_side = 0
for line in lines:
    if not line.strip():
        continue
    f = line.split()
    ts = f[0]
    status = int(f[5])
    if 500 <= status <= 599 and "2026-09-25T22:10:00Z" <= ts < "2026-09-25T23:00:00Z":
        window += 1
        if status in (502, 504):
            gateway_side += 1

forms = [
    "%d 5xx" % window,
    "%d failed" % window,
    "%d errors" % window,
    "%d 5xx" % gateway_side,
    "%d failed" % gateway_side,
    "%d errors" % gateway_side,
]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
