# DISTILL-CANARY-6e9c4111 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '959fa67fd4b5ee3d5773ca53670ca527853cc67a764e0f16c89a8d904e6a806a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["我电脑上的松针办公是 12.3，现在正式版是多少了？要不要升？"], item
print(json.dumps({"expected_string": "12.6"}, ensure_ascii=False))
