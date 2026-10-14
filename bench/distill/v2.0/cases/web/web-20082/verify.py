# DISTILL-CANARY-0e6b25fd : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9a2302227fdb3c6f760b4831b1e3c7cd6412ccef8354e7f9ce4a62aedfb7cc98', "fixture changed"
txt = case["files"]['财务/汇率备忘.txt']
m = re.search('2026-08-28 美元兑人民币 中间价 (7\\.1342)', txt)
print(json.dumps({"expected_string": m.group(1)}, ensure_ascii=False))
