# DISTILL-CANARY-62981699 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'cac200c0006fd433868ae10a9bd18725d36f9e6827ab938dc8f68661aa059f78', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in turn["prompt"], item
print(json.dumps({"expected_contains_any": ["2026-09-28", "2026/9/28", "2026年9月28日", "2026 年 9 月 28 日", "9月28日", "9 月 28 日", "9月28号", "September 28", "28 September", "Sep 28", "28 Sep", "28.9.2026", "September 28, 2026", "Sep 28, 2026", "28/09/2026", "09/28/2026", "2026/09/28", "2026.09.28", "2026-11-14", "2026/11/14", "2026年11月14日", "2026 年 11 月 14 日", "11月14日", "11 月 14 日", "11月14号", "November 14", "14 November", "Nov 14", "14 Nov", "14.11.2026", "November 14, 2026", "Nov 14, 2026", "14/11/2026", "11/14/2026", "2026.11.14"]}, ensure_ascii=False))
