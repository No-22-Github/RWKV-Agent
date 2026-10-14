# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'b458647f242eceb38dc2fdd052e07bc52eb3b2073fc56b12ea9668ac0d52eb1f', "fixture changed"
text = case["files"]['jobs/nightly/last_run.log']
assert '0' in case["files"]['last_run.log']
assert '137' in text
print(json.dumps({"expected_string": '137'}, ensure_ascii=False))
