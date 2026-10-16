# DISTILL-CANARY-7688c966 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bd44c5e338136696c3056746f24d5cdfe0796d796315985f873a98a41f296188', "fixture changed"
page = " ".join(w["content"] for w in case["web_fixture"])
assert '3.9.1' in page
assert '3.9.1' in case["turns"][0]["expect"]["output_contains"]
print(json.dumps({"expected_string": '3.9.1'}, ensure_ascii=False))
