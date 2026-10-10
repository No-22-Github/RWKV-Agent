# DISTILL-CANARY-abfeaa99 : distillation case
import ast
import json
import re

case = json.load(open("case.json"))
readme = case["files"]["README.md"].splitlines()
head = re.match('^# liyun_control —— 规范源文件：(\\S+)；', readme[0] if readme else "")
if head is None:
    raise SystemExit("fixture guard failed: README must open with the canonical source line")
source_path = head.group(1)
if source_path not in case["files"]:
    raise SystemExit("fixture guard failed: canonical source missing")
source = case["files"][source_path].splitlines()
defs = [i + 1 for i, line in enumerate(source) if re.match(r"def push_frame_cmd\(", line)]
if len(defs) != 1:
    raise SystemExit("fixture guard failed: push_frame_cmd defined %d times" % len(defs))
hits = [i + 1 for i, line in enumerate(source) if "push_frame_cmd" in line]
if len(hits) < 3:
    raise SystemExit("fixture guard failed: 名称回声缺失")

print(json.dumps({"expected_number": defs[0]}))
