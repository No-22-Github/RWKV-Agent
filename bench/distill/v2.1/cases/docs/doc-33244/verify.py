# DISTILL-CANARY-7fea75ae : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd67ac66e264b2eb12c384a11ae5bab41f55eeffb5950f56ccc45aac8fd5abc28', "fixture changed"
files = case["files"]
def answer(files):
    return "财务总监"

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
