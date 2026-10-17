# DISTILL-CANARY-b9cf389d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["去鹭岛的白沙渡轮现在末班几点？官方时刻表和旅游攻略写的不一样。", "那首班呢？"], item
print(json.dumps({"expected_string": "17:30"}, ensure_ascii=False))
