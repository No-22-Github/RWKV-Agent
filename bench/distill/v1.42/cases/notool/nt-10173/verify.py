# DISTILL-CANARY-1248ce0a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2f1889895442c4e3113a03aa2ba6fcf3a57c66d57464e2a9ac324c9a7ff2595b', "fixture changed"
print(json.dumps({"expected_contains_any": ["du -sh", "du -h", "du -s"]}, ensure_ascii=False))
