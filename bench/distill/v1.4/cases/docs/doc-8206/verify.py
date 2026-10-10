# DISTILL-CANARY-b4fb3d7d : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == 'f9b25420250e5fbe4f5a29f54a09b1a24f6205517f8fe251a8566e8858827988'
ans = re.search(r"开始前 (\d+) 小时以上", files["排练室/使用说明.md"]).group(1)
assert ans == '24'
print(json.dumps({"expected_contains_any": ['24 小时', '24 个小时', '24小时', '24个小时']}, ensure_ascii=False))
