# DISTILL-CANARY-97c51387 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '4a3d49611afe24f64fea78f85cf4e43c52c0d6180c63f81f7f25a081f3d3ef99'
ans = re.search(r"玫瑰：每 (\d+) 天", files["养护/鲜切花.md"]).group(1)
assert ans == '2'
print(json.dumps({"expected_contains_any": ['每 2 天', '每2天', '2 天换', '2天换', '隔 2 天', '两天']}, ensure_ascii=False))
