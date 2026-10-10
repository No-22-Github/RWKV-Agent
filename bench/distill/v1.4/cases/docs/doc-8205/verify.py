# DISTILL-CANARY-0d64f96d : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '7f07a6ee0073a6988170e23f6ec94fd56b46d7c5d934b923b2dabe5fcc48a033'
ans = re.search(r"换屏：保修 (\d+) 天", files["店规/保修.md"]).group(1)
assert ans == '90'
print(json.dumps({"expected_contains_any": ['90 天', '90 日', '90天', '90日']}, ensure_ascii=False))
