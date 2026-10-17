# DISTILL-CANARY-30f0a063 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'fe103cc39082e073bafe73ba9afbec7c306c444a6145e4e5940d9cdbd9b5f4ad', "fixture changed"
answers=['22:13']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
