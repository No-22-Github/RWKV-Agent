# DISTILL-CANARY-517d09e2 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0acfb208c417184e9c5781113a780318922634a4f8e78795fefa901703a05194', "fixture changed"
m = re.search('会议号：([\\d ]+)', case["files"]['会议链接.md'])
assert m and m.group(1) == '123 456 789'
print(json.dumps({"expected_string": '123 456 789'}, ensure_ascii=False))
