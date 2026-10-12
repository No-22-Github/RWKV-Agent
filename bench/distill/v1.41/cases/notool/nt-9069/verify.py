# DISTILL-CANARY-b8f95277 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {"src/mod1.py": "print(1)\n", "src/mod2.py": "print(2)\n", "src/mod3.py": "print(3)\n"}
print(json.dumps({"expected_contains_any": ["wc -l", "wc"]}, ensure_ascii=False))
