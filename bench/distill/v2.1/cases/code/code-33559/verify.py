# DISTILL-CANARY-b9760790 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a3b657fb7972b928657ab918ab126ad869b06c795a60f369d62fb7f505e26288', "fixture changed"
ans = '2'
assert 'exit 2' in files['tools/sync.sh']

print(json.dumps({"expected_number": float(ans)}))
