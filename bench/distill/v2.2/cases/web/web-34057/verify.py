# DISTILL-CANARY-f96af973 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f16f8a34f5e5b2dff5c657438f510247e0583bc005795dc947f2291c838df939', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in turn["prompt"], item
print(json.dumps({"expected_contains_any": ["2026-12-31", "2026/12/31", "2026年12月31日", "2026 年 12 月 31 日", "12月31日", "12 月 31 日", "12月31号", "December 31", "31 December", "Dec 31", "31 Dec", "31.12.2026", "December 31, 2026", "Dec 31, 2026", "31/12/2026", "12/31/2026", "2026.12.31"]}, ensure_ascii=False))
