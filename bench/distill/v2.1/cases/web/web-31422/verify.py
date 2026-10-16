# DISTILL-CANARY-7fde4af4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6cfbb1d3a8d23fa92b15fb6cd83df29c0426593eaab30a2eaa573cb85c2100bf', "fixture changed"
page = " ".join(w["content"] for w in case["web_fixture"])
assert '18 USD' in page
assert '18 USD' in case["turns"][0]["expect"]["output_contains"]
print(json.dumps({"expected_string": '18 USD'}, ensure_ascii=False))
