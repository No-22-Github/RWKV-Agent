# DISTILL-CANARY-1f3e2e31 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '89548f05db3606ed9ce2deb23bd281172e74e62b92a5be33ac0dc49bdd185cd1'
ans = [p for p, t in sorted(files.items()) if "增氧机停转" in t][0]
assert ans == '日志/塘B.log'
print(json.dumps({"expected_contains_any": ['塘B', '塘 B', 'B 塘', 'B塘']}, ensure_ascii=False))
