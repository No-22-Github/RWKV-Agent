# DISTILL-CANARY-2238553d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["紫藤药房免配送费要满多少钱？他们的服务说明和活动页写得不一样，先说结论，再说为什么。"], item
print(json.dumps({"expected_string": "29"}, ensure_ascii=False))
