# DISTILL-CANARY-47ab567d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e21c71a9c592e42d9584a0f16bbdf7569a1f4a9f42ee1a2965b898de5b8f2290', "fixture changed"
text = case["files"]['制度/差旅标准.md']
assert '650' in text
print(json.dumps({"expected_string": '650'}, ensure_ascii=False))
