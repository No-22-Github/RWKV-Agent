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

_cg = case["files"].get('logs/ci-builds.log', "")
if '2026-09-26 13:05:12 BR-3300 repo=nav-stack result=failed stage=sim-tests worker=ci-05 error="timeout in grasp planner"' not in _cg:
    raise SystemExit(1)
print(json.dumps({"expected_number": len(failed)}))
