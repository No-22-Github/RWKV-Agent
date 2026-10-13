# DISTILL-CANARY-d0233cc0 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a36f425ba1629042a766209d9378670a2fd51c62f9922c5f2846934044f7999a', "fixture changed"
text = case["files"]['apps/billing/settings.toml']
assert '3' in case["files"]['settings.toml']
assert '7' in text
print(json.dumps({"expected_string": '7'}, ensure_ascii=False))
