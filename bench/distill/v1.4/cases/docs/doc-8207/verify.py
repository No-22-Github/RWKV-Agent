# DISTILL-CANARY-9302844b : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '302047df7f7a1a3c00984bb8cebf90c952bc40de006be81c21bd209338a78c6a'
ans = re.search(r"Every pull request needs (\d+) approvals", files["guides/review-rules.md"]).group(1)
assert ans == '2'
print(json.dumps({"expected_contains_any": ['2 approvals', 'two approvals', 'Two approvals']}, ensure_ascii=False))
