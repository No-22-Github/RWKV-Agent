# DISTILL-CANARY-eaa902a6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["云麓出行的退票手续费，官方公告和一个论坛帖子说的不一样。哪个是官方的、哪个更新？到底怎么收费？先给结论。"], item
print(json.dumps({"expected_string": "20%"}, ensure_ascii=False))
