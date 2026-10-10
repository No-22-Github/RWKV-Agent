# DISTILL-CANARY-a6beff52 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '54f7bad9738ae353309a19ba1bad2bd89cc4b813cfcddb422a7ac0e9a997bb9f'
ans = re.search(r"\| Economy \| (\d+) kg", files["guide/services.md"]).group(1)
assert ans == '20'
print(json.dumps({"expected_number": 20}))
