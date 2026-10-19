# DISTILL-CANARY-0e1f1c29 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1c08f269e7bf102f988d2a8a1bdde8f8ef3f5ee85e4293ce3d91e47282d6e657', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in turn["prompt"], item
print(json.dumps({"expected_contains_any": ["2026-11-15", "2026/11/15", "2026年11月15日", "2026 年 11 月 15 日", "11月15日", "11 月 15 日", "11月15号", "November 15", "15 November", "Nov 15", "15 Nov", "15.11.2026", "November 15, 2026", "Nov 15, 2026", "15/11/2026", "11/15/2026", "2026.11.15"]}, ensure_ascii=False))
