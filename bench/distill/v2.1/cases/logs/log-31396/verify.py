# DISTILL-CANARY-1e210049 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a8d9bbd8cdd13b0367a7dd08775b8f4c31f09321909401434c46a67e58e42547', "fixture changed"
import re
m = re.search('可用性 (99\\.62)%', case["files"]['status/uptime-2026-09.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
