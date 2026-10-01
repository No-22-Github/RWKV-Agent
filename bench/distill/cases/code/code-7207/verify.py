# DISTILL-CANARY-eef0ee70 : distillation case
import ast
import json
import re

case = json.load(open("case.json"))
readme = case["files"]["README.md"].splitlines()
head = re.match('^# pineburst — Canonical source: (\\S+);', readme[0] if readme else "")
if head is None:
    raise SystemExit("fixture guard failed: README must open with the canonical source line")
source_path = head.group(1)
if source_path not in case["files"]:
    raise SystemExit("fixture guard failed: canonical source missing")
source = case["files"][source_path].splitlines()
defs = [i + 1 for i, line in enumerate(source) if re.match(r"def drain_queue\(", line)]
if len(defs) != 1:
    raise SystemExit("fixture guard failed: drain_queue defined %d times" % len(defs))
if any(re.match(r'def drain_queue\(', line)
       for line in case['files']['pineburst/queuectl2.py'].splitlines()):
    raise SystemExit('fixture guard failed: queuectl2 must not define the function')
print(json.dumps({"expected_number": defs[0]}))
