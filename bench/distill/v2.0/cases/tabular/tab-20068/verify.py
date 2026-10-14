# DISTILL-CANARY-82334511 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c6ae91724f8b1d3443787f3fdd435ebe690ca2ecd54f1cb13f67501fc2bf349a', "fixture changed"
m = re.search('(路由器),3,10', case["files"]['inventory.csv'])
assert m and m.group(1) == '路由器'
m = re.search('(光模块),2,12', case["files"]['inventory.csv'])
assert m and m.group(1) == '光模块'
print(json.dumps({"expected_string": '路由器'}, ensure_ascii=False))
