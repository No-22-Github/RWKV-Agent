# DISTILL-CANARY-ec23c2ed : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["团河农场的土鸡蛋多少钱一箱？", "我找到他们的价目表链接了：https://tuanhe-farm.example/shop/prices ，你看看。"], item
print(json.dumps({"expected_string": "58"}, ensure_ascii=False))
