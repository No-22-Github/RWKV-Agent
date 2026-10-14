# DISTILL-CANARY-913c0cd3 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'b03288e969f5d985a39d132b67e9b3d4b66a67744571b13331c5e2ed2611b96c', "fixture changed"
m = re.search('2026-09-12 杭州 多云 24~(33)℃', case["files"]['出差/天气记录.md'])
print(json.dumps({"expected_string": m.group(1)}, ensure_ascii=False))
