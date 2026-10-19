# DISTILL-CANARY-6ccb1130 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '81b3ac90e98d857d758b8154f8ac9e453cbf26ef183817156ed151eab19fa527', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in turn["prompt"], item
print(json.dumps({"expected_contains_any": ["2027-04-30", "2027/4/30", "2027年4月30日", "2027 年 4 月 30 日", "4月30日", "4 月 30 日", "4月30号", "April 30", "30 April", "Apr 30", "30 Apr", "30.4.2027", "April 30, 2027", "Apr 30, 2027", "30/04/2027", "04/30/2027", "2027/04/30", "2027.04.30"]}, ensure_ascii=False))
