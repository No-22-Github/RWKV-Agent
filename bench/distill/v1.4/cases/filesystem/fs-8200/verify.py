# DISTILL-CANARY-5198fb8a : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '75424672bb0f21f1f5746e10778059988a00e9909633f0c35c4d781e5f01e179'
ans = len([p for p in files if p.startswith("盘点/") and p.count("/") == 1 and p.endswith(".csv")])
assert ans == 3
print(json.dumps({"expected_contains_any": ['3 个', '3 份', '3 张', '3个', '3份', '3张', '三个', '三份']}, ensure_ascii=False))
