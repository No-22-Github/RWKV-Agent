# DISTILL-CANARY-ecf7675e : distillation case
import hashlib
import json

case = json.load(open("case.json"))
assert hashlib.sha256(json.dumps(case["files"], sort_keys=True, ensure_ascii=False).encode()).hexdigest().startswith('ef909a11e4b72bb3')
print(json.dumps({"expected_contains_any": ["没有", "没写", "未给", "没给", "缺", "尚未", "还没", "未确定", "未明确", "不明确", "未提供", "不存在", "找不到", "冲突", "不一致", "矛盾"]}, ensure_ascii=False))
