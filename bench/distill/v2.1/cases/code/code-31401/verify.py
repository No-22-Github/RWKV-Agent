# DISTILL-CANARY-95f96d99 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3f3b6eabd053ed6f9a666c867dc8406cce9684c58488bda174951c028d85202c', "fixture changed"
import re
m = re.search("batch-size', type=int, default=(\\d+)", case["files"]['tools/cli.py'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
