# DISTILL-CANARY-13046679 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9abd27b8d8c13b9f0f3c02a65689b1f60a0785096a603bfb31a02b0bb56ac2d9', "fixture changed"
files = case["files"]
def answer(files):
    import re
    return re.search(r"\| Japan \| (\d+) \|", files["finance/per-diem.md"]).group(1)

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
