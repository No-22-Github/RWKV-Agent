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

_cg = case["files"].get('logs/db-slowquery.log', "")
if '2026-09-23 05:14:26 dur=6.4s db=reporting user=bi_dash query="SELECT week, channel, sum(spend) FROM marketing GROUP BY 1, 2"' not in _cg:
    raise SystemExit(1)
print(json.dumps({"expected_number": slow}))
