# DISTILL-CANARY-87e7f523 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '366e494b4d5009fa38b952aa3ce4d2d54869705b2ad17c91f9fb7bdd11538a2a', "fixture changed"
print(json.dumps({"expected_contains_any": ["reset --soft"]}, ensure_ascii=False))
