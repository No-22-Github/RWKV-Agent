# DISTILL-CANARY-040da9b5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0daffb484825ebe69c9f9ebe60a10921d7c8ae00f2cdf36a784da7bc950163d1', "fixture changed"
import re
ans = re.search('总额 (\\d+) 万', case["files"]['minutes/0912-财务.md']).group(1)
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert '380' in case['turns'][1]['expect']['output_contains']
assert str(ans) == '380'
