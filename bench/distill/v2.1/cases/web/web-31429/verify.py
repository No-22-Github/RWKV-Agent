# DISTILL-CANARY-b44dd030 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'edcdf9ebfe21a187551b542d128259ae1792aefe4ee4fba8c5daf44dd6020691', "fixture changed"
page = " ".join(w["content"] for w in case["web_fixture"])
assert '1.8.5' in page
assert '1.8.5' in case["turns"][0]["expect"]["output_contains"]
print(json.dumps({"expected_string": '1.8.5'}, ensure_ascii=False))
