# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '52f37c1f933d8debdd24ad8678e3c99e26bf359179ad309074f1784913eeda48', "fixture changed"
text = case["files"]['门店/杭州西湖店/营业时间.txt']
assert '22:00' in case["files"]['营业时间.txt']
assert '23:30' in text
print(json.dumps({"expected_string": '23:30'}, ensure_ascii=False))
