# DISTILL-CANARY-d0723484 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '95802d93f33208cdea90a3b074df7188c67889ff4448025bdd2fa06d1cb986c8', "fixture changed"
import re
ans = re.search('Attendees: (Priya)', case["files"]['reviews/review-2026-09-15.md']).group(1)
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert 'Priya' in case['turns'][1]['expect']['output_contains']
assert str(ans) == 'Priya'
