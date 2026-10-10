# DISTILL-CANARY-ed3a1c80 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '903f6690e3916c16558f7744dc57a85fb28cd345dd5bcbaebf91cfeee13354f0'
ans = re.search(r"up to (\d+) guests per month", files["handbook/guests.md"]).group(1)
assert ans == '3'
print(json.dumps({"expected_number": 3}))
