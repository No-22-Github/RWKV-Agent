# DISTILL-CANARY-0fa8f424 : distillation case
import hashlib
import json

case = json.load(open("case.json"))
assert hashlib.sha256(json.dumps(case["files"], sort_keys=True, ensure_ascii=False).encode()).hexdigest().startswith('9fb4dc7d4387bf9a')
print(json.dumps({"expected_contains_any": ["冲突", "矛盾", "不一致", "两张", "两份", "互相", "不同的值", "不同"]}, ensure_ascii=False))
