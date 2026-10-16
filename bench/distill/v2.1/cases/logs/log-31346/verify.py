# DISTILL-CANARY-b5270beb : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9717f2a58cde4c1f79fa274193ad0c97f23fb48270a0303bcc61e923e554a13f', "fixture changed"
ans = str(sum(1 for l in case["files"]['logs/pay-a-0912.log'].splitlines() if " FAIL " in l))
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert '14' in case['turns'][1]['expect']['output_contains']
assert str(ans) == '14'
