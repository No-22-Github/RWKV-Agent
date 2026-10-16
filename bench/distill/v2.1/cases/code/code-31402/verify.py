# DISTILL-CANARY-795daeb2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a7899062099c2536d13f63affb232a3fb72974fac330494ce348cb3866345436', "fixture changed"
import re
m = re.search("'E207': '([a-z ]+)'", case["files"]['core/errors.py'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
