# DISTILL-CANARY-d31d9dd3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '928a9bb4d71ba4c19b159dd6fd4195680550412ce21d5f31e6cc8fa0842518e9', "fixture changed"
import re
ls = [l for l in files['logs/storefront-nginx-0914.log'].split('\n') if l]
c = 0
for l in ls:
    m = re.search(r'\[[^:]+:(\d\d):(\d\d):\d\d [^\]]*\] "[^"]*" (\d+) ', l)
    if m and m.group(3) == '500' and m.group(1) == '09' and int(m.group(2)) < 30:
        c += 1
answers = [c]

KINDS = ['i']
DPS = [2]

def forms(v, dp):
    if dp == 0:
        s = str(int(round(v)))
        out = [s]
        if abs(int(s)) >= 1000:
            out.append("{:,}".format(int(s)))
        return out
    s = "%.*f" % (dp, v)
    whole, _, frac = s.partition(".")
    out = [s, "{:,}".format(int(whole)) + "." + frac if int(whole) else s]
    t = s.rstrip("0").rstrip(".")
    out.append(t)
    if int(whole) >= 1000:
        out.append("{:,}".format(int(whole)) + "." + frac.rstrip("0") if frac.rstrip("0") else "{:,}".format(int(whole)))
    return list(dict.fromkeys(out))
out = []
for k, dp, a in zip(KINDS, DPS, answers):
    out += [x for x in forms(a, 0 if k == 'i' else dp) if x not in out]
print(json.dumps({"expected_contains_any": out}, ensure_ascii=False))
