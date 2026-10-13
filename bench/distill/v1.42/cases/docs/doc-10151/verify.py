# DISTILL-CANARY-dd1e7a12 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '094349a3f48344ced0850c4fccfe1606d29b61eab7af8fcf83123ccc12e68ce3', "fixture changed"
text = case["files"]['项目/合同审批/进度.md']
assert '立项' in case["files"]['进度.md']
assert '法务复核' in text
print(json.dumps({"expected_string": '法务复核'}, ensure_ascii=False))
