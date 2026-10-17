# DISTILL-CANARY-c181d745 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a1c4ab099e699a9ab7a8189090543a1181b73620d1456b49ef7d041deb76275f', "fixture changed"
files = case["files"]
def answer(files):
    import re
    return str(round(120 * float(re.search(r"按 ([\d.]+) 元/公里", files["行政/公车管理.md"]).group(1))))

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
