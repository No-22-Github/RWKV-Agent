# DISTILL-CANARY-afc0dd4a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1355be7e043c9494241e85c30a4c82aef58b345fc5930926e3159413010e1c99', "fixture changed"
files = case["files"]
def answer(files):
    return "30 minutes" if "Premium plan get P2 first response of 30 minutes" in files["support/sla.md"] else ""

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
