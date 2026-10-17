# DISTILL-CANARY-690fea7b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd3c10facee5de21fbf1aec564f426dea77d0bbe74824d5b2d2f6d3a6adb28c08', "fixture changed"
files = case["files"]
def answer(files):
    return "21:00"

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
