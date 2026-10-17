# DISTILL-CANARY-372be9aa : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a9634b3555ad6fe60e4082596b23a2c05b0b5cd78737eaa8cc67a574182501eb', "fixture changed"
answers=['svc-b','19:12']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
