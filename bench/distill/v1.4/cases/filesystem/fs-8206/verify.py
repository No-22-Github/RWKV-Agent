# DISTILL-CANARY-f60bb585 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == 'ee054b4e80a4f9a1c937291b015fd8c13d04b1d090f5a42f2cbddf58cf6f1753'
ans = len([p for p in files if p.startswith("shoot-0412/") and p.endswith(".cr2")])
assert ans == 5
print(json.dumps({"expected_number": 5}))
