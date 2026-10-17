# DISTILL-CANARY-6ad4a762 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["梧桐驿站入住前几天内取消要收费？"], item
print(json.dumps({"expected_contains_any": ["3 天", "3天", "三天", "3 days", "three days"]}, ensure_ascii=False))
