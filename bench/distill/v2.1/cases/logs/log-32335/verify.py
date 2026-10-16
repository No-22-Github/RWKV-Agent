# DISTILL-CANARY-69f5ff54 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd20b99e8a1ef96fd9262756c1ac7fb517f53532554b5bfc21a884be40b1133f7', "fixture changed"
ans = sum(1 for l in files['hosts.log'].splitlines() if any(k in l for k in ('panic:', 'OOM-killed', 'SIGSEGV')))
print(json.dumps({"expected_number": float(ans)}, ensure_ascii=False))
