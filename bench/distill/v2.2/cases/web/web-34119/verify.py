# DISTILL-CANARY-c52f2040 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
prompts = " ".join(t["prompt"] for t in case["turns"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in prompts or item in [], item
for url in [w["url"] for w in case["web_fixture"]]:
    assert url, url
print(json.dumps({"expected_contains_any": ["2026-10-01", "2026/10/1", "2026年10月1日", "2026 年 10 月 1 日", "10月1日", "10 月 1 日", "10月1号", "October 1", "1 October", "Oct 1", "1 Oct"]}, ensure_ascii=False))
