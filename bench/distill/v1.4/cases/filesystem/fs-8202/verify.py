# DISTILL-CANARY-6651a979 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '9e86996e717cd642a493ed431265997dc28847d489b7f146311d8357737f06ef'
ans = len([p for p in files if p.endswith(".gpx")])
assert ans == 4
print(json.dumps({"expected_contains_any": ['4 条', '4 个', '4 份', '4条', '4个', '4份', '四条', '四个']}, ensure_ascii=False))
