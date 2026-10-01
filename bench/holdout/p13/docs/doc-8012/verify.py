# DISTILL-CANARY-58b2dd3d : p13 holdout eval case (eval-only, never for training)
import json
import re
import sys

case = json.load(open("case.json"))
lines = case["files"]["api-changelog.md"].splitlines()
if not lines or not lines[0].startswith("# 支付接口版本记录"):
    sys.exit(1)
released = []
for line in lines:
    m = re.match(r"\|\s*(v[\d.]+)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(\S+?)\s*\|", line)
    if m and m.group(3) == "已发布":
        released.append((m.group(2), m.group(1)))
if not released:
    sys.exit(1)
released.sort()
print(json.dumps({"expected_string": released[-1][1]}))
