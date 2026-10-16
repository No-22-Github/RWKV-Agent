# DISTILL-CANARY-bca36d7e : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '470cbaa7aa5e52bbc7fe8cd68805fb95aa8a060f1323d8fc41f633c3d44b834c', "fixture changed"
page = " ".join(w["content"] for w in case["web_fixture"])
assert '21:40' in page
assert '21:40' in case["turns"][0]["expect"]["output_contains"]
print(json.dumps({"expected_string": '21:40'}, ensure_ascii=False))
