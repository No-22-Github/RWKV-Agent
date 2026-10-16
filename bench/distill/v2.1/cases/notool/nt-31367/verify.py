# DISTILL-CANARY-40a997ba : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c8b4b89dbc18ce982d953a0f419d02563129657cca6f38659782958e52b7e79d', "fixture changed"
import re
ans = re.search('总额 (\\d+) 万', case["files"]['minutes/0912-财务.md']).group(1)
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert str(ans) in case['turns'][0]['expect']['output_contains']
