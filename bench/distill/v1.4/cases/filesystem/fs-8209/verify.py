# DISTILL-CANARY-5f587fc2 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '82282fb0096873f1ecc72055833dd940732344bd602941f24ce01ad5cf0b5443'
ans = [p for p, t in sorted(files.items()) if "Owner: Priya" in t][0]
assert ans == 'tasks/irrigation.md'
print(json.dumps({"expected_string": 'irrigation'}, ensure_ascii=False))
