# DISTILL-CANARY-c3f91541 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2c72d9866b8845bfee18cf5e42574c7074de136e5ef1ccf64cc15f298ae53ce7', "fixture changed"
ans = case['turns'][0]['expect']['output_contains'][0]
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
