# DISTILL-CANARY-89c7fc42 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["标准错误", "stderr", "标准输出", "stdout", "文件描述符"]}, ensure_ascii=False))
