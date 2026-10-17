# DISTILL-CANARY-3822c0f0 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'adcb81a3e0e1c16edf77d85d29598e68cf2f66b085d8844976ff74316bd56830', "fixture changed"
files = case["files"]
def answer(files):
    import re
    return re.search(r"超过 (\d+) 天的，不予报销", files["财务/发票与报销.md"]).group(1)

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
