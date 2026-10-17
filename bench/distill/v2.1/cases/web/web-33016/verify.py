# DISTILL-CANARY-7f70c491 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["灯塔健身的月卡到底多少钱？官网和点评网站的数字对不上，帮我判断哪个可信，哪个更新。"], item
print(json.dumps({"expected_string": "258"}, ensure_ascii=False))
