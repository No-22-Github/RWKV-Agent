# DISTILL-CANARY-dfa93aa8 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '560389b206c48df5a9124d000e5338b291c9e2dcdc291998ebebbd25b22977ea'
ans = max(re.findall(r"站点-(\d{8})\.csv", " ".join(files)))
assert ans == '20260920'
print(json.dumps({"expected_contains_any": ['20260920', '2026-09-20', '9 月 20 日', '9月20日', '9 月 20 号', '9月20号']}, ensure_ascii=False))
