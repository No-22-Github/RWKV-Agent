# DISTILL-CANARY-bcd1c58b : distillation case
import hashlib
import json

case = json.load(open("case.json"))
assert hashlib.sha256(json.dumps(case["files"], sort_keys=True, ensure_ascii=False).encode()).hexdigest().startswith('31e4fe14bfaed19d')
print(json.dumps({"expected_contains_any": ["另行通知", "没有", "没写", "未给", "没给", "缺", "尚未", "还没", "未确定", "未明确", "不明确", "未提供", "不存在", "找不到", "冲突", "不一致", "矛盾"]}, ensure_ascii=False))
