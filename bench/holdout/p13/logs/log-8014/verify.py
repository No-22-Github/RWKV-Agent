# DISTILL-CANARY-9029c38b : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json
import re
import sys

case = json.load(open("case.json"))
deploys = list(csv.DictReader(io.StringIO(case["files"]["发布记录.csv"])))
prod = [r for r in deploys if r["环境"].strip() == "生产"]
if not prod:
    sys.exit(1)
latest = max(r["开始时间"].strip() for r in prod)
window_start = latest.split(" ", 1)[1]
first_service = None
for line in case["files"]["app-20260918.log"].splitlines():
    m = re.match(r"\S+ (\d{2}:\d{2}):\d{2} \[(\w+)\] (\S+)", line)
    if not m:
        continue
    hhmm, level, token = m.groups()
    if level != "ERROR" or hhmm < window_start:
        continue
    first_service = token
    break
if not first_service:
    sys.exit(1)
print(json.dumps({"expected_string": first_service}))
