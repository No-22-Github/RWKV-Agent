# DISTILL-CANARY-80a886ab : p13 holdout eval case (eval-only, never for training)
import json
import re
import sys

case = json.load(open("case.json"))
lines = case["files"]["周会纪要-0914.md"].splitlines()
if not lines or not lines[0].startswith("# 运营周会纪要"):
    sys.exit(1)
count = 0
for line in lines:
    m = re.match(r"\|[^|]+\|[^|]+\|\s*(\d{4}-\d{2}-\d{2})\s*\|", line.strip())
    if m and m.group(1) <= "2026-09-30":
        count += 1
print(json.dumps({"expected_number": count}))
