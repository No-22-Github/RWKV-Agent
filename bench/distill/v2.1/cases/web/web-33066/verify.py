# DISTILL-CANARY-35a626ca : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["琥珀词典的插件 API v1 什么时候不能用了？我要提前告诉用户。", "那现在还能上架 v1 的新插件吗？"], item
print(json.dumps({"expected_string": "不再"}, ensure_ascii=False))
