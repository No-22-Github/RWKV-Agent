# DISTILL-CANARY-555d2b1d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7fcb8d7f08cb4d9055cf1d286a880fa2b7a541516f7e573317c869bd43910a5d', "fixture changed"
import re
m = re.search('MAX_RETRIES = (\\d+)\\nBACKOFF', case["files"]['src/retry.py'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
