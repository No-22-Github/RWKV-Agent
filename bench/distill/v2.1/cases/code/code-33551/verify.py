# DISTILL-CANARY-4456edfd : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '28b0f02afbb95035c8525f3b9a51cc7bf790fb91b4eeb515beab3073d58adff2', "fixture changed"
n = 6
s = 0
while n != 1:
    n = n // 2 if n % 2 == 0 else 3 * n + 1
    s += 1
ans = str(s)
assert ans == '8'

print(json.dumps({"expected_number": float(ans)}))
