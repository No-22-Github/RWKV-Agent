# DISTILL-CANARY-74a71fce : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4fc8a15925226179abd91c6d0d87b81249e73d3af9bb882d97d02b10b558c33d', "fixture changed"
files = case["files"]
def answer(files):
    import re
    return re.search(r"施工、维修类访客不超过 (\d+) 小时", files["安保/访客规定.md"]).group(1)

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
