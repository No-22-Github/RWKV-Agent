# DISTILL-CANARY-7fc9be03 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["稻香外卖骑手的基础单价是多少，结算周期多久？官网有两份说明，别拿错旧的。"], item
print(json.dumps({"expected_string": "5.5"}, ensure_ascii=False))
