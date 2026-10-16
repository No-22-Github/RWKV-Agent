# DISTILL-CANARY-eecf8f0b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7b77e4291ee967ced54eca5f66715616a3cce603cc0bbdd8cd89d82cdb9587cc', "fixture changed"
import re
m = re.search('port: (\\d+)', case["files"]['config/app.yaml'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
