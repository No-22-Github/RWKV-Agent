# DISTILL-CANARY-3e4ff99a : distillation case
import json
import re

case = json.load(open("case.json"))
n = 0
for line in case["files"]["logs/api-gw/2026-09-15.log"].splitlines():
    assert re.match(r"^2026-09-15 \d\d:\d\d:\d\d \+0800 GET /v1/", line), line
    parts = line.split()
    if parts[1].startswith("09:") and parts[5].startswith("5"):
        n += 1
print(json.dumps({"expected_number": n}))
