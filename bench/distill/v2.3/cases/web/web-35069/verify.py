# DISTILL-CANARY-e4d880c5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '141af8533492b54c83b41d669ddc68a091b5a40991efe0afe14d2a812a293d55', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
prompts = " ".join(t["prompt"] for t in case["turns"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in prompts, item
print(json.dumps({"expected_contains_any": ["2026-09-11", "September 11", "Sep 11", "11 September", "11 Sep", "9/11", "11/09", "11.09"]}, ensure_ascii=False))
