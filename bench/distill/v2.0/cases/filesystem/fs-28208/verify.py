# DISTILL-CANARY-1bdaf756 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '66268a5325dacffe4553180fda29baf8343df832f023af0d5163b974f38d489d'
ans = len([p for p in files if re.fullmatch(r"scripts/ep\d+\.md", p)])
assert ans == 4
print(json.dumps({"expected_contains_any": ['4 ', 'four', 'Four', '4.', '4 episode', '4 script']}, ensure_ascii=False))
