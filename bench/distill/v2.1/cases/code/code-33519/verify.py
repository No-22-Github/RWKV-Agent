# DISTILL-CANARY-70f61928 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '842ea2589aeec966bf2bd3a50e261ef52dcb73ba415fdc93d7d05ba252dba0f7', "fixture changed"
import re
name = 'check_zip'
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
assert sorted(out) == ['app/forms/shipping.py', 'app/forms/signup.py'], out
ans = 'app/forms/signup.py'

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
