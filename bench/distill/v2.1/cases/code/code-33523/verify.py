# DISTILL-CANARY-4a13b0c2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a51d231a103171fe03f947fc056ecc4a9f0882ae5fb13553f1883476af8ba619', "fixture changed"
import re
name = 'fetchUser'
out = []
for p, t in sorted(files.items()):
    for l in t.split(chr(10)):
        s = l.strip()
        if s.startswith(('#', '//', '*', '/*')) or re.match(r'(export )?(async )?(def|func|function) ', s):
            continue
        s = re.sub(r"(\"[^\"]*\"|'[^']*')", '', s)
        if re.search(r'\b' + name + r'\(', s):
            out.append(p)
            break
assert sorted(out) == ['web/pages/admin.ts', 'web/pages/profile.ts'], out
ans = 'web/pages/profile.ts'

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
