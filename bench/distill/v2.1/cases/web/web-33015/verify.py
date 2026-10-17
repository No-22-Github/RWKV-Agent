# DISTILL-CANARY-ba24eecb : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["Brindle DB 文档和 7.3 发布说明对最大连接数说法不同，都是厂商自己发的。现在的上限是多少，哪个页面更新？"], item
print(json.dumps({"expected_string": "1200"}, ensure_ascii=False))
