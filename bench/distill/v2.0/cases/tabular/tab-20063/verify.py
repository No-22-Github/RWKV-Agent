# DISTILL-CANARY-9aa7f478 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e0d7282607b8d7ff130d736090572d71ecfee44407195a1807cc09603e99cbc7', "fixture changed"
m = re.search('(bo\\.chen@[\\w.]+),no', case["files"]['attendees.csv'])
assert m and m.group(1) == 'bo.chen@harbor.example'
m = re.search('(ivy\\.liu@[\\w.]+),no', case["files"]['attendees.csv'])
assert m and m.group(1) == 'ivy.liu@harbor.example'
print(json.dumps({"expected_string": 'bo.chen@harbor.example'}, ensure_ascii=False))
