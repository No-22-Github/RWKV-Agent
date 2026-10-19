# DISTILL-CANARY-73429798 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '87b4c7eb4418275a2047cfbc8065e4b536ac8fb77d1034064759952e0471557a', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in turn["prompt"], item
print(json.dumps({"expected_contains_any": ["idle", "Idle", "timeout", "Timeout", "空闲", "超时"]}, ensure_ascii=False))
