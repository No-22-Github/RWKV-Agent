# DISTILL-CANARY-0f77f7e9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c3f261926947ce9b05b54167d44b6dcd96d1724125aa0c2beb64a14318b53c87', "fixture changed"
import re
m = re.search('(cache key format)', case["files"]['postmortems/release-3.8.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
