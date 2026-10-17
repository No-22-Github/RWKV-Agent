# DISTILL-CANARY-0b9c176e : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["漠河云服务的经典网络要退役了吗？我现在还能新建吗？"], item
print(json.dumps({"expected_contains_any": ["2027-06-30", "2027/6/30", "2027年6月30日", "2027 年 6 月 30 日", "6月30日", "6 月 30 日", "6月30号", "June 30", "30 June", "Jun 30", "30 Jun", "30.6.2027"]}, ensure_ascii=False))
