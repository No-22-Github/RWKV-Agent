# DISTILL-CANARY-488a9a96 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9d9c22b116c22b6a003279347e0844687f1ec745f977c5bb04a954753521ef48', "fixture changed"
args = ['data/a.txt', 'data/x.txt', 'data/y.txt', 'data/z.txt']
ex = {'data/a.txt', 'data/b.txt'}
ans = str(sum(1 for a in args if a not in ex))
assert ans == '3'

print(json.dumps({"expected_number": float(ans)}))
