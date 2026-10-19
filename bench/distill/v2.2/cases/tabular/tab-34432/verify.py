# DISTILL-CANARY-3a5f5241 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '916658009b4e0e043965759c36b0a0e1c7bbeb1d8c3e6aefefed32ccb20b0f4c', "fixture changed"
import csv, io, collections
rows = list(csv.DictReader(io.StringIO(files['售后/退款对账明细-q2.csv']), delimiter=','))
cents = lambda x: round(float(x) * 100)
rf = [x for x in rows if x['settle_state'] == 'refunded']
answers = [len([x for x in rf if float(x['gross']) > 500]), sum(cents(x['gross']) for x in rf) / 100.0]

KINDS = ['i', 'f']
DPS = [2, 2]

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
