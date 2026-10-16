# DISTILL-CANARY-a63b97e9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5aae95ec94d4f4f9a0d6594156e4255b2b5a2d3e13852ca72b5997ffb810c66d', "fixture changed"
import re
m = re.search('max_items_per_page\\": (\\d+)', case["files"]['config/features.json'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
