# DISTILL-CANARY-b067c3c3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e14a9f70fc5a9ee8405ecb37bfaeee2abcac574aae3cfd485104fd34da4f58b5', "fixture changed"
page = case["web_fixture"][0]["content"]
assert case["files"]['deps/README.md'].startswith('# Dependencies')
assert '--legacy-auth' in page
print(json.dumps({"expected_contains_any": ["--legacy-auth", "legacy-auth"]}, ensure_ascii=False))
