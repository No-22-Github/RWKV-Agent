# DISTILL-CANARY-36100335 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '604e48b81a47e2b0cc1a649d4872e991c4803e28a241e7938688d5cfcc78be29', "fixture changed"
ans = str(sum(1 for l in case["files"]['logs/auth-tue.log'].splitlines() if " WARN " in l))
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert '11' in case['turns'][1]['expect']['output_contains']
assert str(ans) == '11'
