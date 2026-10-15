# EXAM-CANARY-35b8ad5c : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
import re
c = {}
for l in case["files"]["logs/worker.log"].splitlines():
    k = re.search(r"\[(\w+)\]", l).group(1)
    c[k] = c.get(k, 0) + 1
print(json.dumps({"expected_contains_all": [str(v) for v in c.values()]}))
