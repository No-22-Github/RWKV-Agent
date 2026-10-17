# DISTILL-CANARY-6907a541 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '48815e5970d274c5fdee3ae17e75b391271070644666a1e924644b52f0626440', "fixture changed"
s=[p for p in files if p.startswith('src/')]
m=max(s,key=lambda p:len(files[p].encode()))
m2=max((p for p in s if not p.endswith('_test.go')),key=lambda p:len(files[p].encode()))
answers=[m.split('/')[-1],m2.split('/')[-1]]
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
