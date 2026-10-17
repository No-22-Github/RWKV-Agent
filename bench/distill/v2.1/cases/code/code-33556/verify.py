# DISTILL-CANARY-7487576c : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'efd891d9bd535b5fa2dae343405b7ced5529dc3c780e742435f6344b46fec56e', "fixture changed"
tokens, ok = 5, 0
for _ in range(7):
    if tokens >= 1:
        tokens -= 1
        ok += 1
first = ok
tokens = min(5, tokens + 2)
ok = 0
for _ in range(4):
    if tokens >= 1:
        tokens -= 1
        ok += 1
assert first == 5 and ok == 2, (first, ok)
ans = str(first)

print(json.dumps({"expected_number": float(ans)}))
