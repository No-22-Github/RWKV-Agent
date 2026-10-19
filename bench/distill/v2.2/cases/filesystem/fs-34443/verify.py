# DISTILL-CANARY-38104100 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6c6accdf8ab422258b025adb2980480f7a3e9dd5df7f7d398ecbc8b459e57788', "fixture changed"
answers = [len([p for p in files if files[p].split('\n')[0] >= 'updated: 2026-09-01'])]

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
