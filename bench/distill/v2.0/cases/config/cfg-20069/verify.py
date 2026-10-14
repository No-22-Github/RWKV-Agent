# DISTILL-CANARY-dde62005 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6a44537a98b3f6e272182fd2b470eae3f43eabd5c6cda7c27fc220d938ba80d5', "fixture changed"
m = re.search('name: (Sam Okafor)', case["files"]['oncall.yaml'])
assert m and m.group(1) == 'Sam Okafor'
m = re.search('phone: \\"([+\\d-]+)\\"', case["files"]['oncall.yaml'])
assert m and m.group(1) == '+1-555-0142'
print(json.dumps({"expected_string": 'Sam Okafor'}, ensure_ascii=False))
