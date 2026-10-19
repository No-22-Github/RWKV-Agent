# DISTILL-CANARY-ac8f884b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ade54d612c0f5add7b14fe1525b57043e771a321774e653be86975dfa27b7f17', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in turn["prompt"], item
print(json.dumps({"expected_contains_any": ["2027-03-31", "2027/3/31", "2027年3月31日", "2027 年 3 月 31 日", "3月31日", "3 月 31 日", "3月31号", "March 31", "31 March", "Mar 31", "31 Mar", "31.3.2027", "March 31, 2027", "Mar 31, 2027", "31/03/2027", "03/31/2027", "2027/03/31", "2027.03.31", "push", "Push"]}, ensure_ascii=False))
