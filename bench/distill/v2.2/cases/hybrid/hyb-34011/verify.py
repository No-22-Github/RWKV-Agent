# DISTILL-CANARY-c6f291a1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5a403b86a753426a1d30f3a903234cf3ae2443c45d4c649f1433ea5d0670ca49', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in turn["prompt"], item
print(json.dumps({"expected_contains_any": ["2026-09-17", "2026/9/17", "2026年9月17日", "2026 年 9 月 17 日", "9月17日", "9 月 17 日", "9月17号", "September 17", "17 September", "Sep 17", "17 Sep", "17.9.2026", "September 17, 2026", "Sep 17, 2026", "17/09/2026", "09/17/2026", "2026/09/17", "2026.09.17"]}, ensure_ascii=False))
