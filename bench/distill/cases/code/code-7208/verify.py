# DISTILL-CANARY-2afbc965 : distillation case
import ast
import json
import re

case = json.load(open("case.json"))
readme = case["files"]["README.md"].splitlines()
head = re.match('^# hanmo_sync —— 规范源文件：(\\S+)；', readme[0] if readme else "")
if head is None:
    raise SystemExit("fixture guard failed: README must open with the canonical source line")
source_path = head.group(1)
if source_path not in case["files"]:
    raise SystemExit("fixture guard failed: canonical source missing")
source = case["files"][source_path].splitlines()
defs = [i + 1 for i, line in enumerate(source) if re.match(r"def sync_ledger\(", line)]
if len(defs) != 1:
    raise SystemExit("fixture guard failed: sync_ledger defined %d times" % len(defs))
near_defs = [i + 1 for i, line in enumerate(source) if re.match(r'def sync_ledger_cache\(', line)]
if len(near_defs) != 1:
    raise SystemExit('fixture guard failed: 近名函数应恰好定义一次')
print(json.dumps({"expected_number": defs[0]}))
