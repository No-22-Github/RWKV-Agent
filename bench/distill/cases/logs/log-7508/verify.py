# DISTILL-CANARY-f98da5ee : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/db-slowquery.log"].splitlines()

slow = 0
best = 0.0
for line in lines:
    m = re.search(r"dur=([\d.]+)s", line)
    if not m:
        continue
    dur = float(m.group(1))
    if dur > 5.0:
        slow += 1
        best = max(best, dur)

forms = ["%d 条" % slow, "%s" % best]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
