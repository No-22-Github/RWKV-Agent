# DISTILL-CANARY-dc8af188 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a86d39ebb6f49c904588a9c1212fcc2b827ccd56f45f91d5a7a6726584bf221c', "fixture changed"
print(json.dumps({"expected_contains_any": ["wc -l"]}, ensure_ascii=False))
