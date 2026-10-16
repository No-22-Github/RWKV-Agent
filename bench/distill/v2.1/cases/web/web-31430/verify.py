# DISTILL-CANARY-de998043 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '14f4bf86bc8217b33442f8d95a23676da180442d6725168a953a0248867a0264', "fixture changed"
page = " ".join(w["content"] for w in case["web_fixture"])
assert '8:00-22:00' in page
assert '8:00-22:00' in case["turns"][0]["expect"]["output_contains"]
print(json.dumps({"expected_string": '8:00-22:00'}, ensure_ascii=False))
