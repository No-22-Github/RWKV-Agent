# DISTILL-CANARY-4c7c9d2c : p13 holdout eval case (eval-only, never for training)
import json
import re
import sys

case = json.load(open("case.json"))
lines = case["files"]["deploy-20260914.log"].splitlines()
m = re.search(r"开始发布 (\S+) (v[\d.]+)", lines[0]) if lines else None
if not m:
    sys.exit(1)
service, version = m.group(1), m.group(2)
marker = f"{service} {version} 部署完成"
start = None
for i, line in enumerate(lines):
    if marker in line:
        start = i
        break
if start is None:
    sys.exit(1)
for line in lines[start + 1:]:
    if "[ERROR]" in line:
        tm = re.match(r"\S+ (\d{2}:\d{2})(?::\d{2})?", line)
        if tm:
            print(json.dumps({"expected_string": tm.group(1)}))
        break
