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

forms = [cause, cause,
         "%d builds" % len(ci04), "%d failed" % len(ci04), "%d failures" % len(ci04),
         "%d build" % ci04_real, "%d failed" % ci04_real, "%d failure" % ci04_real]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
