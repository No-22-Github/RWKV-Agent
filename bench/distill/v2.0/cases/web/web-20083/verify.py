# DISTILL-CANARY-c876ebbe : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4ad82049b3bfd107f432c2c25d0f1741afb1551d8d8986e6e243d60cbe1d802b', "fixture changed"
txt = case["files"]['采购/报价记录.md']
m = re.search('2026-07-22 \\| 4C8G \\| (296) 元', txt)
print(json.dumps({"expected_string": m.group(1)}, ensure_ascii=False))
