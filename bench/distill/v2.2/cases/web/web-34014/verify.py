# DISTILL-CANARY-1091faf2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1d806ab0342780b2ce5a9947c80679bc0ce979b5b797d88ca8424a49e8849a66', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in turn["prompt"], item
print(json.dumps({"expected_contains_any": ["2026-12-31", "2026/12/31", "2026年12月31日", "2026 年 12 月 31 日", "12月31日", "12 月 31 日", "12月31号", "December 31", "31 December", "Dec 31", "31 Dec", "31.12.2026", "December 31, 2026", "Dec 31, 2026", "31/12/2026", "12/31/2026", "2026.12.31"]}, ensure_ascii=False))
