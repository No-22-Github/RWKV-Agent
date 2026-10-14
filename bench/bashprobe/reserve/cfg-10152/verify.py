# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd26224505f6f3c027910446cc7d8ee72bf4d997a94ebc86141831cd9ff0cafd6', "fixture changed"
text = case["files"]['deploy/staging/values.yaml']
assert '1.8.0' in case["files"]['values.yaml']
assert '1.9.0-rc2' in text
print(json.dumps({"expected_string": '1.9.0-rc2'}, ensure_ascii=False))
