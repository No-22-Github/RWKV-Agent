# DISTILL-CANARY-344ad5e7 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '7f5bac30ce855b11295aa9a546864f146169f01972c050ec57754658a8a0479c'
ans = json.loads(files["equipment/freezers.json"])["F-80A"]["alarm_c"]
assert ans == -70
print(json.dumps({"expected_number": -70}))
