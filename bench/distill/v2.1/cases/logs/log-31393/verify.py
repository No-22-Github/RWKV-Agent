# DISTILL-CANARY-4319a62c : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '555fadafd08d90698a141692cb9939b45fb58806d3469aeee9215bea3e722c11', "fixture changed"
import re
m = re.search('timeout after (\\d+) ms', case["files"]['logs/app.log'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
