# DISTILL-CANARY-5c05671e : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c44b62a50eda598f419980abaee31ec02810381e3ed68c18e06b4e61256640f0', "fixture changed"
import re
name = 'ParseToken'
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
assert sorted(out) == ['internal/auth/token_test.go', 'internal/http/middleware.go', 'internal/ws/upgrade.go'], out
ans = 'internal/http/middleware.go'

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
