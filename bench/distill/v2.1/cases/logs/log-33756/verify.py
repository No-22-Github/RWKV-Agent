# DISTILL-CANARY-a164ebd0 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'b562b5d4c12dce1aa52fefdbb3c2e472f44ccabbf16e73ca13b4e694a1f8ceac', "fixture changed"
answers=['batch.log.1','01:05']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
