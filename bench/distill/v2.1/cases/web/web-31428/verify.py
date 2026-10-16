# DISTILL-CANARY-8e2e7bac : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2eaa365d2c5c9a974a81291831c97f7e27d8aee3d37b5eb2189cd55584514959', "fixture changed"
page = " ".join(w["content"] for w in case["web_fixture"])
assert '12 元' in page
assert '12 元' in case["turns"][0]["expect"]["output_contains"]
print(json.dumps({"expected_string": '12 元'}, ensure_ascii=False))
