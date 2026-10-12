# DISTILL-CANARY-3826b5e5 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["辐射", "散热", "热量", "保温", "吸收", "反射", "温室"]}, ensure_ascii=False))
