# DISTILL-CANARY-7101465c : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a853fb5afc5916f3b7f9ab7a5d01697783c31c16b323ad516963fd1f819d393d', "fixture changed"
import re
ans = re.search('for (\\d+) seconds', case["files"]['manuals/camera.md']).group(1)
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert '10' in case['turns'][1]['expect']['output_contains']
assert str(ans) == '10'
