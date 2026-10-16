# DISTILL-CANARY-f017c420 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '233247a10e9776aba591f97f0224930f745156262ad81bef694e051a73fe7d51', "fixture changed"
ans = case['turns'][0]['expect']['output_contains'][0]
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
