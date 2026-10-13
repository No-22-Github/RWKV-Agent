# DISTILL-CANARY-c2ca9778 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'b003fda3163dc2559358aa23cd0ef69c320d3cc761edec791a8a1a810e6d1662', "fixture changed"
print(json.dumps({"expected_contains_any": ["0 9 * * 1-5"]}, ensure_ascii=False))
