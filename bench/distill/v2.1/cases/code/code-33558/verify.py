# DISTILL-CANARY-d65ce7ed : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1919107ac375d3f8a21796ea7a9e7365f363a77433c496bf6a86ee2d997a2989', "fixture changed"
s = 'ab'
while len(s) < 5:
    s += '*'
ans = s
assert ans == 'ab***' and 'abcdef'[:4] == 'abcd'

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
