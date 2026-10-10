# DISTILL-CANARY-b1899c0d : distillation case
import hashlib
import json

case = json.load(open("case.json"))
assert hashlib.sha256(json.dumps(case["files"], sort_keys=True, ensure_ascii=False).encode()).hexdigest().startswith('6c86f2c63cea5a41')
print(json.dumps({"expected_contains_any": ["按后厨主管口头通知", "没有", "没写", "未给", "没给", "缺", "尚未", "还没", "未确定", "未明确", "不明确", "未提供", "不存在", "找不到", "冲突", "不一致", "矛盾"]}, ensure_ascii=False))
