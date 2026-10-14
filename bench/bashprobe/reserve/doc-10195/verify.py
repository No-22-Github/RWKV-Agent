# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'b36d21f26aecad2536a47d0783f38a74e8a72e423b485127575e8800e9b577dd', "fixture changed"
text = case["files"]['docs/SLA.md']
assert '15 minutes' in text
print(json.dumps({"expected_string": '15 minutes'}, ensure_ascii=False))
