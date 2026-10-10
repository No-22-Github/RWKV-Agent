# DISTILL-CANARY-c272a14b : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '59db2cc9078f997fa0cb869a961c62950c44256b49472dc3e9a0b10d0ab5a8cd'
ans = re.search(r"attend at least (\d+)%", files["handbook/certificates.md"]).group(1)
assert ans == '80'
print(json.dumps({"expected_contains_any": ['80%', '80 %', '80 percent', 'eighty percent']}, ensure_ascii=False))
