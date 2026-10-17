# DISTILL-CANARY-4c531e6f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1bc082a405b71350e76935bcaaa17de03b04e90d257491ba8eb97eaf0d9985ab', "fixture changed"
files = case["files"]
def answer(files):
    import re
    return re.search(r"\n- 超过 3 天：提前 (\d) 个工作日", files["制度/假期制度.md"]).group(1)

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
