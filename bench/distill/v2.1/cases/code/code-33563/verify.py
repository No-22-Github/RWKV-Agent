# DISTILL-CANARY-06a1b8de : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2141b8d025b142ef4c223175a7951bb57fd8319b4f3e6de93403dfdff0b58b72', "fixture changed"
ans = 'ports must be unique'
assert 'not ok 3 - ports must be unique' in files['test/out.tap']

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
