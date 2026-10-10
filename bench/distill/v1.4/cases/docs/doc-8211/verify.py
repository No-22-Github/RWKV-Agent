# DISTILL-CANARY-ac20dbfd : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == 'e31569d8d87f96d1f766be78af2b1ca3a7f13efe3aaf5f48b7438bf2b0ae582e'
ans = re.search(r"(\d+) minutes before departure for foot", files["faq/boarding.md"]).group(1)
assert ans == '30'
print(json.dumps({"expected_contains_any": ['30 minutes', '30 min', 'half an hour', 'half hour', '30-minute']}, ensure_ascii=False))
