# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '585c416f47313c0905cc3f33b83d405c8c2371d9d039e452e7bb7fb66aced98f', "fixture changed"
text = case["files"]['插件/导出/版本.txt']
assert '3.2.0' in case["files"]['版本.txt']
assert '0.9.4' in text
print(json.dumps({"expected_string": '0.9.4'}, ensure_ascii=False))
