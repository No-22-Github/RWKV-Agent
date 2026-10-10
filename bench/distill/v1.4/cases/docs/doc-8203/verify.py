# DISTILL-CANARY-b2ce7de3 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == 'cae23396652200f826819029e20f9809673e9986454dfbab8125845e551a9388'
ans = re.search(r"学生座位 (\d+) 个", files["校车/运行手册.md"]).group(1)
assert ans == '16'
print(json.dumps({"expected_contains_any": ['16 个', '16 名', '16 位', '16个', '16名', '16位']}, ensure_ascii=False))
