# DISTILL-CANARY-2ccbf5c7 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1aea3199c45376a520e70a9d48374b2a2e52704c8a6fae5e85050a4c39fc55a6', "fixture changed"
page = " ".join(w["content"] for w in case["web_fixture"])
assert '23 kg' in page
assert '23 kg' in case["turns"][0]["expect"]["output_contains"]
print(json.dumps({"expected_string": '23 kg'}, ensure_ascii=False))
