# DISTILL-CANARY-2b38d144 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd4fc776b0639dfd1ab0ca49e5e61cf4ca45b54e90f7938d5091d4f4d1c4b8fce', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in turn["prompt"], item
print(json.dumps({"expected_contains_any": ["configuration", "Configuration", "config", "Config", "配置"]}, ensure_ascii=False))
