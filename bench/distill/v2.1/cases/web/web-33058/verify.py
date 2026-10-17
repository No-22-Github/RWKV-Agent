# DISTILL-CANARY-283c6d1a : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["烟火通知的短信 v1 接口是不是要下线了？什么时候，换成什么？"], item
print(json.dumps({"expected_contains_any": ["2026-12-31", "2026/12/31", "2026年12月31日", "2026 年 12 月 31 日", "12月31日", "12 月 31 日", "12月31号", "December 31", "31 December", "Dec 31", "31 Dec", "31.12.2026"]}, ensure_ascii=False))
