# DISTILL-CANARY-72da3ae6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '67a005019b79943546bd7f7590a0b7045b18dc5bd0a136d6c574e1799601e1e5', "fixture changed"
import re
m = re.search('replicas: (\\d+)', case["files"]['deploy/prod.yaml'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
