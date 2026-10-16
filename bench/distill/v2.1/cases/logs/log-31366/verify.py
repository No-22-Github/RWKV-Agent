# DISTILL-CANARY-a08947e1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '18b8e0bf960a5077a7ddfdd31585ad4ff8b101decb895c540f70329ff05bfbd1', "fixture changed"
ans = [l for l in case["files"]["logs/deploy.log"].splitlines()][-1].split()[0]
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert str(ans) in case['turns'][0]['expect']['output_contains']
