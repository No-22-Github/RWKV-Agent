# DISTILL-CANARY-8fa71583 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == 'cb9ef1a7d881e43cf75effecd85f965c8f870fea6d7a4f09fdc31181d19d8be6'
ans = re.search(r"签收后 (\d+) 小时", files["条款/服务条款.md"]).group(1)
assert ans == '48'
print(json.dumps({"expected_contains_any": ['48 小时', '48 个小时', '48 h', '48小时', '48个小时', '48h']}, ensure_ascii=False))
