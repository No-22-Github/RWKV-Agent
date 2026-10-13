# DISTILL-CANARY-6d9ef112 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '13b02be7373fb96a9f61488c0baaf175c53d6e67ff9eb8da066ee9d7ab3d5ee9', "fixture changed"
prompt = case["turns"][0]["prompt"]
want = ["8443"]
assert all(w in prompt for w in want)
print(json.dumps({"expected_contains_any": want}, ensure_ascii=False))
