# DISTILL-CANARY-7002ba8c : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5be67bbec55f105241bdf23b8204e699e76b17c2ffedf9f3de5d315ccf8ec37e', "fixture changed"
m = re.search('(wang\\.lei@[\\w.]+)', case["files"]['contacts.csv'])
assert m and m.group(1) == 'wang.lei@lanting.example'
m = re.search('(12\\.6%)', case["files"]['report.md'])
assert m and m.group(1) == '12.6%'
print(json.dumps({"expected_string": 'wang.lei@lanting.example'}, ensure_ascii=False))
