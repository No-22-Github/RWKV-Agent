# DISTILL-CANARY-cf33367d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["浮光云盘最近发了个套餐调整公告，帮我看下说了啥，列一下要点。", "那团队版怎么迁移？他们好像有说明页，帮我看看。"], item
print(json.dumps({"expected_string": "500"}, ensure_ascii=False))
