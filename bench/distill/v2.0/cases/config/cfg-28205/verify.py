# DISTILL-CANARY-4149e3dc : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '46d44613bc6e70510bfe6351a6dc1cf7e18929aba30b5b5fce1102b66e62b094'
ans = json.loads(files["studio/policy.json"])["late_cancel_fee"]
assert ans == 35
print(json.dumps({"expected_contains_any": ['35 元', '35 块', '35元', '35块']}, ensure_ascii=False))
