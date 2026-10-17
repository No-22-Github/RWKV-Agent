# DISTILL-CANARY-c7aace26 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '07c17517ba2bc4ea49fabfd86b89024af01f0d99b14f1a8f74848b6582e99a95', "fixture changed"
files = case["files"]
def answer(files):
    import re
    return re.search(r"客服录音 \| (\d+) 天", files["it/数据保留规定.md"]).group(1)

V = answer(files)
inc = [x for t in case["turns"] for x in t["expect"].get("output_contains", [])]
assert V in inc, (V, inc)
print(json.dumps({"expected_string": V}, ensure_ascii=False))
