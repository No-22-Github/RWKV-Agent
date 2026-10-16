# DISTILL-CANARY-337a4bbe : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f8ec8436d3ba6b1adf563043fa0a9f78b978ef84a43b47aa9665329ff6555c4f', "fixture changed"
import re
m = re.search('体检预算 (\\d+) 元，取代', case["files"]['hr/benefits-v2.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
