# DISTILL-CANARY-7a7811de : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == 'f11ea1fcef3157cfce8e375b8ea9c32ac1416713290fe3e633d1e0b57bd3096f'
ans = [p for p, t in sorted(files.items()) if re.search(r"^RATE_LIMIT_PER_MIN =", t, re.M)][0]
assert ans == 'src/limits.py'
print(json.dumps({"expected_string": 'src/limits.py'}, ensure_ascii=False))
