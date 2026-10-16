# DISTILL-CANARY-a070845c : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '53f146eb7a4fa3b6ce3c247f3e1ed07ab3541ed87ae0b9667b553003b0f9b6d3', "fixture changed"
ans = str(sum(1 for l in case["files"]['logs/app-0915.log'].splitlines() if " ERROR " in l))
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert '12' in case['turns'][1]['expect']['output_contains']
assert str(ans) == '12'
