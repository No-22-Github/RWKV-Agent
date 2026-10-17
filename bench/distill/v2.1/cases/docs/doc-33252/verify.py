# DISTILL-CANARY-0bf5725f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'abb81f86b09a111e14b373c35a57f382d851a53947bf81c1df71c3dda207dce9', "fixture changed"
files = case["files"]
def answer(files):
    return "500"

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
