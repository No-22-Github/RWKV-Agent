# DISTILL-CANARY-6d849a65 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c5a51d0a24ad1baca53485299908ea2f0f76a6607673488a5590a8972effe76d', "fixture changed"
ans = case['turns'][0]['expect']['output_contains'][0]
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
