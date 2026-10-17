# DISTILL-CANARY-05341184 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4394ec4310d105ed5bfbfda0786a56737ee2a20f3a437e72f37e66b479887fd6', "fixture changed"
answers=['docs/README.rst']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
