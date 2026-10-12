# DISTILL-CANARY-ce0e1ccb : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["成功", "退出码", "前一个", "失败", "返回值", "状态"]}, ensure_ascii=False))
