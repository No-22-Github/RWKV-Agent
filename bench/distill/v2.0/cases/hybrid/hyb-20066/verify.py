# DISTILL-CANARY-08ee3986 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0f1032612da5713c9f84b869ce84a2cda68a2ddd8387196656e181fcaaf6afcb', "fixture changed"
m = re.search('(SF1042938571)', case["files"]['快递单.md'])
assert m and m.group(1) == 'SF1042938571'
m = re.search('电话：(\\d+)', case["files"]['快递单.md'])
assert m and m.group(1) == '95338'
print(json.dumps({"expected_string": 'SF1042938571'}, ensure_ascii=False))
