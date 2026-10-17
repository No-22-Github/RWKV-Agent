# DISTILL-CANARY-0dc9278b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '076ff247ffd8b4934f7c9390f2aaf451ed8a8116e3ccf59140cdaafe3046bcf5', "fixture changed"
files = case["files"]
def answer(files):
    import re
    return re.search(r"电子产品：签收后 (\d+) 天内", files["商城/退换货政策.md"]).group(1)

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
