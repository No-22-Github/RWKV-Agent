# DISTILL-CANARY-75b55b63 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c6523a76121051527ac49b662c30b6a949314435a09ed593179d778a12c80062', "fixture changed"
m = re.search('Release (v[\\d.]+)', case["files"]['release-notes.md'])
assert m and m.group(1) == 'v2.4.1'
draft = 'Team: v2.4.1 is out. It fixes the login timeout and speeds up exports.\n'
assert all(s in draft for s in ['v2.4.1'])
print(json.dumps({"files": {'announcement.md': draft}}, ensure_ascii=False))
