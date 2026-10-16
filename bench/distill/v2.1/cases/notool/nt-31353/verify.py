# DISTILL-CANARY-cf47acb9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'cfb6c8f2ebd4b1e358abf8ba1b5690b1c44780e1e54f76fac1302a9ae163be6a', "fixture changed"
import re
ans = re.search('工作年限：(\\d+) 年', case["files"]['resumes/李四.md']).group(1)
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert '12' in case['turns'][1]['expect']['output_contains']
assert str(ans) == '12'
