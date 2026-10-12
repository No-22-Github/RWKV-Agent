# DISTILL-CANARY-c5a6b413 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["所有者", "属主", "拥有者", "rwx", "读", "可执行", "执行"]}, ensure_ascii=False))
