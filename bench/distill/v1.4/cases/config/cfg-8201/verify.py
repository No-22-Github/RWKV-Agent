# DISTILL-CANARY-434437a2 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == '6ddc4681d56d27a8c7287cd29d9b3fe6633a83998c28102092e2923ad1451f4e'
ans = int(re.search(r"单次时长分钟: (\d+)", files["灌溉/大棚B.yaml"]).group(1))
assert ans == 12
print(json.dumps({"expected_contains_any": ['12 分钟', '12 min', '12 分', '12分钟', '12min', '12分']}, ensure_ascii=False))
