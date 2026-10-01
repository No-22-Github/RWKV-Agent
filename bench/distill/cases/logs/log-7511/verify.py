# DISTILL-CANARY-35667db7 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/ci-builds.log"].splitlines()

failed = []
first_sim = ""
for line in lines:
    if "result=failed" not in line:
        continue
    f = line.split()
    build = f[2]
    stage = ""
    worker = ""
    for part in f[3:]:
        if part.startswith("stage="):
            stage = part.split("=")[1]
        if part.startswith("worker="):
            worker = part.split("=")[1]
    failed.append((build, stage, worker))
    if stage == "sim-tests" and not first_sim:
        first_sim = build

no_ci04 = [b for b, s, w in failed if w != "ci-04"]
forms = [
    "%d 次" % len(failed),
    "%d 次" % sum(1 for b, s, w in failed if s == "sim-tests"),
    first_sim,
    "%d 次" % len(no_ci04),
]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
