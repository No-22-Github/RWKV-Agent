# DISTILL-CANARY-ea1aff6d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c7fb639de22ffc0516b17661c19b3c83cf752962dd942963c8414b35a0207e4a', "fixture changed"
page = " ".join(w["content"] for w in case["web_fixture"])
assert '6.4.2' in page
assert '6.4.2' in case["turns"][0]["expect"]["output_contains"]
print(json.dumps({"expected_string": '6.4.2'}, ensure_ascii=False))
