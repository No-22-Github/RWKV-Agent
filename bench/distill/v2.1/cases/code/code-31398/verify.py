# DISTILL-CANARY-3f073b5f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '52cd46576dc5b6ddbe44a0ddaa5146e5649a975f45d5bcd413301272dc2042d2', "fixture changed"
import re
m = re.search('TOKEN_TTL_HOURS = (\\d+)', case["files"]['app/auth.py'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
