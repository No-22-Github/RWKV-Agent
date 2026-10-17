# DISTILL-CANARY-290a9f14 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7ed343717446f29cdf7ffbd245127d3bd67e5538af3a4ece39e196f15b399ca8', "fixture changed"
files = case["files"]
def answer(files):
    import re
    return re.search(r"B座202）：最多提前 (\d+) 天", files["行政/会议室预订.md"]).group(1)

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
