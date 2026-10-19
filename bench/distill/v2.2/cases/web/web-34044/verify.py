# DISTILL-CANARY-d17f177e : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd50e853930f0c9b9ea3d3432ab864d9ac66947b6ae1165109486ee72970e075d', "fixture changed"
text = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in text or item in turn["prompt"], item
print(json.dumps({"expected_contains_any": ["2027-06-30", "2027/6/30", "2027年6月30日", "2027 年 6 月 30 日", "6月30日", "6 月 30 日", "6月30号", "June 30", "30 June", "Jun 30", "30 Jun", "30.6.2027", "June 30, 2027", "Jun 30, 2027", "30/06/2027", "06/30/2027", "2027/06/30", "2027.06.30"]}, ensure_ascii=False))
