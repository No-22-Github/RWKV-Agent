# DISTILL-CANARY-5a9c414f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a5f25c71e06a13fd820b329d9e925d1c64097c44f23ecef7363598dffb863803', "fixture changed"
page = " ".join(w["content"] for w in case["web_fixture"])
assert '2026-09-08' in page
assert '2026-09-08' in case["turns"][0]["expect"]["output_contains"]
print(json.dumps({"expected_string": '2026-09-08'}, ensure_ascii=False))
