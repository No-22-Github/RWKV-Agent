# DISTILL-CANARY-2eca0df3 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {"data/a.bin": "x\n", "data/b.bin": "y\n", "data/sub/c.bin": "z\n"}
print(json.dumps({"expected_contains_any": ["sort -", "-S"]}, ensure_ascii=False))
