# DISTILL-CANARY-5becb869 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '33951303079e1f3a2b0686e064990a78763e692fef88b546f396b668ac1b3f9c', "fixture changed"
m = re.search('(hr-leave@[\\w.]+)', case["files"]['员工名单.md'])
assert m and m.group(1) == 'hr-leave@lanting.example'
m = re.search('(2026-09-28)', case["files"]['请假.md'])
assert m and m.group(1) == '2026-09-28'
print(json.dumps({"expected_string": 'hr-leave@lanting.example'}, ensure_ascii=False))
