# DISTILL-CANARY-264f4a7d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["海棠课堂上课时弹出 V-322，是什么问题？"], item
print(json.dumps({"expected_contains_any": ["2 台", "2台", "两台", "两个设备", "2 个设备", "2 devices", "two devices"]}, ensure_ascii=False))
