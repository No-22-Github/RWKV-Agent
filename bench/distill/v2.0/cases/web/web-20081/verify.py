# DISTILL-CANARY-2de34e5c : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd292043c7835baed04554ebdd2ca2de5202470bd922b225373eda0b8bea24da3', "fixture changed"
txt = case["files"]['notes/依赖版本.md']
m = re.search('查过 vite，当时最新是 (5\\.1\\.4)', txt)
print(json.dumps({"expected_string": m.group(1)}, ensure_ascii=False))
