# DISTILL-CANARY-fdec7daa : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0f2432cae22b47b46334e8de6f122205b790cc7b4e47f5b946399afe8ec6958c', "fixture changed"
import re
tot = 0
for p, t in files.items():
    if p.startswith('src/'):
        for l in t.split(chr(10)):
            if re.search(r'(//|/\*)\s*(TODO|FIXME|HACK)\b', l):
                tot += 1
ans = tot
assert ans == 6, ans

print(json.dumps({"expected_number": float(ans)}))
