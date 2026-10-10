# DISTILL-CANARY-b67dab32 : distillation case
import json
import re

case = json.load(open("case.json"))
readme = case["files"]["README.md"].splitlines()
head = re.match(r"^# shardkeeper .*Canonical source: (\S+);", readme[0] if readme else "")
if head is None:
    raise SystemExit("fixture guard failed: README must open with the canonical source line")
source_path = head.group(1)
if source_path not in case["files"]:
    raise SystemExit("fixture guard failed: canonical source missing")
source = case["files"][source_path].splitlines()
defs = [i + 1 for i, line in enumerate(source) if re.match(r"def route_shard\(", line)]
if len(defs) != 1:
    raise SystemExit(f"fixture guard failed: route_shard defined {len(defs)} times")
print(json.dumps({"expected_number": defs[0]}))
