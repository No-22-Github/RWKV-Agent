# DISTILL-CANARY-9607c622 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9f9580a3537692282a2401c1dd113d9b2f0e3da2b62692dcc0c2a4b2ecc2ab36', "fixture changed"
ans = [l for l in case["files"]["logs/worker.log"].splitlines() if "restarting" in l][-1].split()[1][:5]
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert '05:02' in case['turns'][1]['expect']['output_contains']
assert str(ans) == '05:02'
