# DISTILL-CANARY-73b8467d : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/ci-builds.log"].splitlines()

cause = ""
ci04 = []
ci04_real = 0
for line in lines:
    if "result=failed" not in line:
        continue
    m = re.search(r'error="(.*)"', line)
    if "BR-3308" in line and m:
        m2 = re.search(r"libedge-[\d.]+", m.group(1))
        if m2:
            cause = m2.group(0)
    if "worker=ci-04" in line:
        ci04.append(line)
        if "channel=nightly-experimental" not in line:
            ci04_real += 1

_cg = case["files"].get('logs/ci-builds.log', "")
if '2026-09-27 10:20:03 BR-3307 repo=slam-maps result=passed stage=sim-tests worker=ci-03 channel=nightly' not in _cg:
    raise SystemExit(1)
print(json.dumps({"expected_number": len(ci04)}))
