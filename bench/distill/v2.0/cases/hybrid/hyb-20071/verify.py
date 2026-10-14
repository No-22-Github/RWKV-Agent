# DISTILL-CANARY-cc20a23c : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e4313a3429292ed2ed66004c4556eb0e2224cefb8b414697de6dfc3f8e564336', "fixture changed"
m = re.search('日期：(2026-09-23)', case["files"]['出差.md'])
assert m and m.group(1) == '2026-09-23'
m = re.search('→ (上海虹桥)', case["files"]['出差.md'])
assert m and m.group(1) == '上海虹桥'
print(json.dumps({"expected_string": '2026-09-23'}, ensure_ascii=False))
