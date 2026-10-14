# DISTILL-CANARY-ad797bb7 : distillation case
import ast
import json
import re

case = json.load(open("case.json"))
readme = case["files"]["README.md"].splitlines()
head = re.match('^# tidewatch — Canonical source: (\\S+);', readme[0] if readme else "")
if head is None:
    raise SystemExit("fixture guard failed: README must open with the canonical source line")
source_path = head.group(1)
if source_path not in case["files"]:
    raise SystemExit("fixture guard failed: canonical source missing")
source = case["files"][source_path].splitlines()
defs = [i + 1 for i, line in enumerate(source) if re.match(r"def calibrate_stream\(", line)]
if len(defs) != 1:
    raise SystemExit("fixture guard failed: calibrate_stream defined %d times" % len(defs))
hits = [i + 1 for i, line in enumerate(source) if "calibrate_stream" in line]
if len(hits) < 4:
    raise SystemExit("fixture guard failed: name echoes missing")

print(json.dumps({"expected_number": defs[0]}))
