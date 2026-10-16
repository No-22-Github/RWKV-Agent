# DISTILL-CANARY-7923931b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bd48e9b7aa4f5587966df5694e0d9c6ee8c5e8939b4ef10ac12fdffcaf3eb5c9', "fixture changed"
import re
m = re.search('函数不超过 (\\d+) 行', case["files"]['standards/code-style.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
