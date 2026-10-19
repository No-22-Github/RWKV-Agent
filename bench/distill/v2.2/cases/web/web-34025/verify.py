# DISTILL-CANARY-90d3e47e : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '87e9ce65f24a979fdac405706bc532394e5a7d9ce3486bd40df1144f596ce34e', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in turn["prompt"], item
print(json.dumps({"expected_contains_any": ["2026-11-30", "2026/11/30", "2026年11月30日", "2026 年 11 月 30 日", "11月30日", "11 月 30 日", "11月30号", "November 30", "30 November", "Nov 30", "30 Nov", "30.11.2026", "November 30, 2026", "Nov 30, 2026", "30/11/2026", "11/30/2026", "2026.11.30"]}, ensure_ascii=False))
