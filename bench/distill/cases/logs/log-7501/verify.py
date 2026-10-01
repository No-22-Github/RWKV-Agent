# DISTILL-CANARY-2f7ac809 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/edge-access.log"].splitlines()

five_xx = set()
checkout = set()
checkout_no_rig = set()
for line in lines:
    if not line.strip():
        continue
    f = line.split()
    status = int(f[5])
    if 500 <= status <= 599:
        five_xx.add(f[1])
        if f[4] == "/checkout":
            checkout.add(f[1])
            if not f[2].startswith("10.42."):
                checkout_no_rig.add(f[1])

_sabotage_guard = case["files"].get('logs/edge-access.log', "")
if not _sabotage_guard.splitlines() or _sabotage_guard.splitlines()[0] != '2026-09-28T21:33:41Z req-6102 10.201.4.12 POST /checkout 502 pay-core 84ms':
    raise SystemExit(1)
print(json.dumps({"expected_number": len(five_xx)}))
