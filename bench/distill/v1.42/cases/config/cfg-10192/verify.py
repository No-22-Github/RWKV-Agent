# DISTILL-CANARY-ec71b7a1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6dc45d8b0b55bb824e635087464d3cdf12606cd358967a1753a1493a9e578f22', "fixture changed"
text = case["files"]['config/app.yaml']
assert '8088' in text
print(json.dumps({"expected_string": '8088'}, ensure_ascii=False))
