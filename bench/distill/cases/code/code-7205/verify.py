# DISTILL-CANARY-c9853cfe : distillation case
import ast
import json
import re

case = json.load(open("case.json"))
readme = case["files"]["README.md"].splitlines()
head = re.match('^# kelpgrid — Canonical source: (\\S+);', readme[0] if readme else "")
if head is None:
    raise SystemExit("fixture guard failed: README must open with the canonical source line")
source_path = head.group(1)
if source_path not in case["files"]:
    raise SystemExit("fixture guard failed: canonical source missing")
source = case["files"][source_path].splitlines()
defs = [i + 1 for i, line in enumerate(source) if re.match(r"def resolve_tenant\(", line)]
if len(defs) != 1:
    raise SystemExit("fixture guard failed: resolve_tenant defined %d times" % len(defs))
near_defs = [i + 1 for i, line in enumerate(source) if re.match(r"def resolve_tenant_id\(", line)]
if len(near_defs) != 1:
    raise SystemExit("fixture guard failed: near-name function expected once")
print(json.dumps({"expected_number": defs[0]}))
