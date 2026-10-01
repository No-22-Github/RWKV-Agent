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

forms = [
    "%d 笔" % len(five_xx),
    "%d 笔" % len(checkout),
    "%d 笔" % len(checkout_no_rig),
]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
