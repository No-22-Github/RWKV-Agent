# DISTILL-CANARY-2c95045f : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {"names.txt": "张三\n李四\n张三\n王五\n李四\n张三\n"}
print(json.dumps({"expected_contains_any": ["uniq -c", "uniq -ic"]}, ensure_ascii=False))
