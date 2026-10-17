# DISTILL-CANARY-f5fde41a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["北屿现在居民第一阶梯水价是多少，10 月以后呢？水务公司网站和市发改局的通知哪个更权威、哪个更新？", "那阶梯的分界线是多少立方米？"], item
print(json.dumps({"expected_string": "3.85"}, ensure_ascii=False))
