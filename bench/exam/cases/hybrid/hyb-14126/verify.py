# EXAM-CANARY-daf6b22d : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
lines = [l.split(" ", 4) for l in case["files"]["var/log/svc-health.log"].splitlines()]
errs = {}
for d, t, svc, lvl, _m in lines:
    if lvl == "ERROR":
        errs.setdefault(svc, []).append(t)
worst = max(errs, key=lambda k: len(errs[k]))
print(json.dumps({"expected_number": len(errs[worst]), "files": {"ops/incident-log.md": case["files"]["ops/incident-log.md"] + "- %s first failed at %s\n" % (worst, errs[worst][0])}}))
