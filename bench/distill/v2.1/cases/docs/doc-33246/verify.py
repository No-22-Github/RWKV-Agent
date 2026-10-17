# DISTILL-CANARY-0bc07858 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2b9d2c4dfb645d792bd0fd2d1e6e4c20709f832c753d53d7dbec274c477ba099', "fixture changed"
files = case["files"]
def answer(files):
    import re
    return re.search(r"总存放量不超过 (\d) L", files["实验室/安全守则.md"]).group(1)

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
