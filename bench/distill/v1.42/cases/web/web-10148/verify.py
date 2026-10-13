# DISTILL-CANARY-6fb9b824 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f78d4e676ab8d4ea34fa83ea7adfc21d0f806d80196829abfc8880ad8b2820c6', "fixture changed"
page = case["web_fixture"][0]["content"]
assert case["files"]['对接/青禾.md'].startswith('# 青禾对接')
assert '600' in page
print(json.dumps({"expected_contains_any": ["600"]}, ensure_ascii=False))
