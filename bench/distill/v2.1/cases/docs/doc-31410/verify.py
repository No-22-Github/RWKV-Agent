# DISTILL-CANARY-cb64a8c1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2e855ee7235ccfc9c542c2fffc905229696c8a69ac00a86755c9c5fc7d9039d2', "fixture changed"
import re
m = re.search('搬迁至 (上海市浦东新区张江路 88 号)', case["files"]['office/address-2026.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
