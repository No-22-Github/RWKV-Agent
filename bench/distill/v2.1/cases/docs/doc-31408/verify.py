# DISTILL-CANARY-ddc5bee4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e2b0029a4bb3ebcaadc8f5a8be2b14ff828b50dc9d19a4a87061e699e52f8798', "fixture changed"
import re
m = re.search('前端负责人：吴迪，分机 (8317)', case["files"]['people/directory.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
