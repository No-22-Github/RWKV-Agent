# EXAM-CANARY-e501b086 : exam gap-fill case
import json
from collections import Counter

case = json.load(open("case.json", encoding="utf-8"))
cnt = Counter()
for line in case["files"]["logs/access.log"].splitlines():
    day, _time, svc, status, _path = line.split()
    if day == "2026-09-14" and status.startswith("5"):
        cnt[svc] += 1
top = cnt.most_common(2)
assert top[0][1] > top[1][1]
print(json.dumps({"expected_string": top[0][0]}))
