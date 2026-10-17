# DISTILL-CANARY-54511505 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '55d4cc0156cad4fb7c967f822a24cbb44110c02f36f73cfa5ac59399bf2d2a5a', "fixture changed"
ans = 'release'
assert 'on: [tag]' in files['.ci/pipeline.yml']

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
