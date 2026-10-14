# DISTILL-CANARY-ed6a608e : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bfb30843b1e3407e8080d86365f9ac27a7e20e98134a242c4f4bde665f3aeeb2', "fixture changed"
print(json.dumps({"expected_string": [p for p, t in case["files"].items() if "8443" in t][0].split("/")[-1]}))
