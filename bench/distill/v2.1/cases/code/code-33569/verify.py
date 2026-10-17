# DISTILL-CANARY-6427f6e4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5705481ef203d2bbf065c2fd1606c0c8122dab4fed614f222f4931ca6092d180', "fixture changed"
ans = '15'
log = files['ci/summary.log']
assert '2 failed, 15 passed, 2 skipped' in log

print(json.dumps({"expected_number": float(ans)}))
