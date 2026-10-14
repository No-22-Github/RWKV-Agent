# DISTILL-CANARY-7e5362a4 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '82414a5909d1a3ea24d6672240c7b5e5697b0f5a5c40e40542b03b818756701b', "fixture changed"
m = re.search('(青禾纸业),QH-0654,30500,待付', case["files"]['发票.csv'])
assert m and m.group(1) == '青禾纸业'
m = re.search(',(30500),待付', case["files"]['发票.csv'])
assert m and m.group(1) == '30500'
draft = '付款申请\n供应商：青禾纸业\n发票号：QH-0654\n金额：30500 元\n'
assert all(s in draft for s in ['青禾纸业', 'QH-0654'])
print(json.dumps({"files": {'付款申请.md': draft}}, ensure_ascii=False))
