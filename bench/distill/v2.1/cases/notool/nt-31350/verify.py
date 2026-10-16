# DISTILL-CANARY-db7c37b4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '50289b2ebcda116c4b29d86fa4d5a724857ca99c4cee5d25db8663ab18b4a65a', "fixture changed"
import re
ans = re.search('Term: (\\d+) months', case["files"]['contracts/vendor-b.md']).group(1)
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert '18' in case['turns'][1]['expect']['output_contains']
assert str(ans) == '18'
