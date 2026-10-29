# DISTILL-CANARY-b41b27ac : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4ddeb10258c1530129635f5be9df8e2652989f541fd700329bd0b2bd0d5f6967', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
prompts = " ".join(t["prompt"] for t in case["turns"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in prompts, item
print(json.dumps({"expected_contains_any": ["2026-08-21", "2026年8月21日", "2026 年 8 月 21 日", "8月21日", "8 月 21 日", "8月21号", "August 21", "21 August", "Aug 21"]}, ensure_ascii=False))
