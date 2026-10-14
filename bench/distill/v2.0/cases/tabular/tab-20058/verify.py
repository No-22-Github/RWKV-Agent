# DISTILL-CANARY-33ec17da : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0ed6c64265dadcf1a9ee6bafaeeeb61552511f8036ba76f5ff3363f7ac780582', "fixture changed"
m = re.search('(远帆包装),FP-0912', case["files"]['发票.csv'])
assert m and m.group(1) == '远帆包装'
m = re.search(',(48600),待付', case["files"]['发票.csv'])
assert m and m.group(1) == '48600'
print(json.dumps({"expected_string": '远帆包装'}, ensure_ascii=False))
