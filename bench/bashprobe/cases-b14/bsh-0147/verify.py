# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9ad40f974a9022af45ca52a41401132fe39cb0e2a64a13fc990ab88eb7a73b09', "fixture changed"
text = case["files"]['服务/订单/限流.yaml']
assert '200' in case["files"]['限流.yaml']
assert '75' in text
print(json.dumps({"expected_string": '75'}, ensure_ascii=False))
