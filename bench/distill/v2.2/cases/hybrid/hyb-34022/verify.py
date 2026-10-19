# DISTILL-CANARY-88153486 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f76f34dc046c346b07ea526acbe7b0aac7984b67d90d881362592426ee0cc449', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in turn["prompt"], item
print(json.dumps({"expected_contains_any": ["2026-09-26", "2026/9/26", "2026年9月26日", "2026 年 9 月 26 日", "9月26日", "9 月 26 日", "9月26号", "September 26", "26 September", "Sep 26", "26 Sep", "26.9.2026", "September 26, 2026", "Sep 26, 2026", "26/09/2026", "09/26/2026", "2026/09/26", "2026.09.26", "2026-09-24", "2026/9/24", "2026年9月24日", "2026 年 9 月 24 日", "9月24日", "9 月 24 日", "9月24号", "September 24", "24 September", "Sep 24", "24 Sep", "24.9.2026", "September 24, 2026", "Sep 24, 2026", "24/09/2026", "09/24/2026", "2026/09/24", "2026.09.24"]}, ensure_ascii=False))
