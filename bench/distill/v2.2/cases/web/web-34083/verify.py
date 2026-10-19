# DISTILL-CANARY-5b3ab1a4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8486b89d592e74f325d70e2564614df67ff5569379da96c2791a0f277e9ea8e8', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in turn["prompt"], item
print(json.dumps({"expected_contains_any": ["2026-12-01", "2026/12/1", "2026年12月1日", "2026 年 12 月 1 日", "12月1日", "12 月 1 日", "12月1号", "December 1", "1 December", "Dec 1", "1 Dec", "1.12.2026", "December 1, 2026", "Dec 1, 2026", "01/12/2026", "12/01/2026", "2026/12/01", "2026.12.01"]}, ensure_ascii=False))
