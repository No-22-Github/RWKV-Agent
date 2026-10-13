# DISTILL-CANARY-beca432d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e154ab255d1461609976ff70c341aa43a137e4c1918e62812dfafdda4f81e7e6', "fixture changed"
print(json.dumps({"expected_contains_any": ["df -h"]}, ensure_ascii=False))
