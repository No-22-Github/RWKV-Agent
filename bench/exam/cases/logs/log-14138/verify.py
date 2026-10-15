# EXAM-CANARY-d51fa10e : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
cnt = {}
for l in case["files"]["logs/service.log"].splitlines():
    p = l.split()
    cnt[p[2]] = cnt.get(p[2], 0) + (1 if p[3] == "ERROR" else 0)
print(json.dumps({"expected_contains_all": [str(v) for v in cnt.values()]}))
