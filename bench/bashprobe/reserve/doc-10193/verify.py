# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9f859837a010ffbb4717b7000c5d1c7b7a03101c29bb090b052d4a24c4d999b3', "fixture changed"
text = case["files"]['会议/周会纪要-0915.md']
assert '10 月 20 日' in text
print(json.dumps({"expected_string": '10 月 20 日'}, ensure_ascii=False))
