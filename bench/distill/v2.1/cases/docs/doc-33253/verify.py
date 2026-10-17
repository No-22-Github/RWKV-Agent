# DISTILL-CANARY-689ed207 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0f5c6bc7252012d33a722b25579a23a0b339ec29195dcb2bc53fec105daecec9', "fixture changed"
files = case["files"]
def answer(files):
    import re
    return re.search(r"中级员工 (\d+) 元", files["hr/培训经费.md"]).group(1)

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
