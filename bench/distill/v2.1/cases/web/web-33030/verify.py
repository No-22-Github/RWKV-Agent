# DISTILL-CANARY-696ac4f2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["银杏社区医院儿科挂号费多少，周几有门诊？", "口腔科挂号费呢？"], item
print(json.dumps({"expected_contains_any": ["8 元", "8元", "8块", "15 元", "15元", "15块"]}, ensure_ascii=False))
