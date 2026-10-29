# DISTILL-CANARY-67d2720f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '520a7846ad3b4885fad77deb6f3ce32405af90901609c474ed5d7e713f58e0dc', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
prompts = " ".join(t["prompt"] for t in case["turns"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in prompts, item
print(json.dumps({"expected_string": "8000"}, ensure_ascii=False))
