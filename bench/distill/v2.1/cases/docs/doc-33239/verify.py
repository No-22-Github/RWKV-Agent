# DISTILL-CANARY-7534943d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6f75209b46cc5f1714be03f8118955e6d593cfc6681e9363939724138c414299', "fixture changed"
files = case["files"]
def answer(files):
    import re
    return re.search(r"二线城市.*?普通员工每晚 (\d+) 元", files["制度/差旅管理办法.md"]).group(1)

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
