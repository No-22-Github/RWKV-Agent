# DISTILL-CANARY-7d005086 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5a0701637713e47370550ddec26197ed97aa8a028e68ffad3d3d5ef1d4c615e9', "fixture changed"
print(json.dumps({"expected_number": sum(1 for p in case["files"] if p.endswith(".md"))}))
