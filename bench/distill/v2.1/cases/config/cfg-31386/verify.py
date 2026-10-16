# DISTILL-CANARY-c13faeb8 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd5be596545187eb43e5bcdf975c5f57894eacd14bdc2f79e0e602d8630698ab7', "fixture changed"
import re
m = re.search('ttl_seconds = (\\d+)', case["files"]['config/cache.toml'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]
assert '3600' not in ans

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
