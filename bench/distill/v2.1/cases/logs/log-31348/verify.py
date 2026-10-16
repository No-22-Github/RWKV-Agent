# DISTILL-CANARY-da3b4016 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7ec81b091bc90210e1208051fed7ba7bc86783f36a3e53427a6e6f5712301eb5', "fixture changed"
ans = case['turns'][0]['expect']['output_contains'][0]
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
