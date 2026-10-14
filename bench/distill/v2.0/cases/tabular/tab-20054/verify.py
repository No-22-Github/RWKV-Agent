# DISTILL-CANARY-c03ace1e : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'af88932e98d79518d22449b8e0c8fa17f6e7897a8a3b7c33f5f6437fa97990e9', "fixture changed"
m = re.search('2026-09-18,([^,\\n]+),', case["files"]['值班表.csv'])
assert m and m.group(1) == '李想'
print(json.dumps({"expected_string": '李想'}, ensure_ascii=False))
