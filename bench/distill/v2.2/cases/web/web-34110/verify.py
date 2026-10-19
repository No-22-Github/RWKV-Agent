# DISTILL-CANARY-731a7b05 : distillation case
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
print(json.dumps({"expected_contains_any": ["2027-03-31", "2027/3/31", "2027年3月31日", "2027 年 3 月 31 日", "3月31日", "3 月 31 日", "3月31号", "March 31", "31 March", "Mar 31", "31 Mar"]}, ensure_ascii=False))
