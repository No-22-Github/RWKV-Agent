# DISTILL-CANARY-6ac108dc : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7ab07310952a215ff95c0b76e085c1ac60267f36c7bced47b816db745b21bab6', "fixture changed"
ans = str(sum(1 for l in case["files"]['logs/app.log'].splitlines() if " ERROR " in l))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert str(ans) in case['turns'][0]['expect']['output_contains']
