# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c1b340c3a7492fd35da804fded51da172ae580432cb76bb0b5ad1a8140e3daf3', "fixture changed"
text = case["files"]['部署/限额.ini']
assert '200' in text
print(json.dumps({"expected_string": '200'}, ensure_ascii=False))
