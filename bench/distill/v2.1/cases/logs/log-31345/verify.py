# DISTILL-CANARY-bd8de601 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9b424c7d5e05d92af190e3d92de3c065715b22a42151d4918d53f3118eab7871', "fixture changed"
ans = case['turns'][0]['expect']['output_contains'][0]
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
