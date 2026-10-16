# DISTILL-CANARY-8b9f306c : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5c8d84cd552785ac21da6a7abd4c69a079094f0c090f9f3ab26015a4a20d0eb5', "fixture changed"
page = " ".join(w["content"] for w in case["web_fixture"])
assert '0.57' in page
assert '0.57' in case["turns"][0]["expect"]["output_contains"]
print(json.dumps({"expected_string": '0.57'}, ensure_ascii=False))
