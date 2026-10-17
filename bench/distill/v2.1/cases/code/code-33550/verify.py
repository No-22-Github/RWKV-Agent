# DISTILL-CANARY-9e4e5028 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e77567304863037a4f52b7f22d8c93e16236d4dea2ebeed2290651c7d9333714', "fixture changed"
xs = list(range(1, 8))
n = 3
ans = len([xs[i:i + n] for i in range(0, len(xs), n)][-1])
assert ans == 1
ans = str(ans)

print(json.dumps({"expected_number": float(ans)}))
