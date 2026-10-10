# DISTILL-CANARY-617f49e0 : distillation case
import ast
import json
import re

case = json.load(open("case.json"))
readme = case["files"]["README.md"].splitlines()
head = re.match('^# moorline — Canonical source: (\\S+);', readme[0] if readme else "")
if head is None:
    raise SystemExit("fixture guard failed: README must open with the canonical source line")
source_path = head.group(1)
if source_path not in case["files"]:
    raise SystemExit("fixture guard failed: canonical source missing")
source = case["files"][source_path].splitlines()
defs = [i + 1 for i, line in enumerate(source) if re.match(r"def trim_history\(", line)]
if len(defs) != 1:
    raise SystemExit("fixture guard failed: trim_history defined %d times" % len(defs))
near_defs = [i + 1 for i, line in enumerate(source) if re.match(r'def trim_history_locked\(', line)]
if len(near_defs) != 1:
    raise SystemExit('fixture guard failed: near-name function expected once')
print(json.dumps({"expected_number": defs[0]}))
